### FILENAME: utils.py ###
import json
import re
import requests
import logging
import hashlib
import base64
from config import OLLAMA_MODEL, OLLAMA_URL

logger = logging.getLogger(__name__)

# --- 1. ROBUST URL CONFIGURATION ---
base_url = OLLAMA_URL.replace("/api/generate", "").replace("/api/chat", "").rstrip("/")
CHAT_ENDPOINT = f"{base_url}/api/chat"
EMBED_ENDPOINT = f"{base_url}/api/embeddings"

# In-Memory Storage
sessions = {}
embedding_cache = {}


# ==========================================
# 2. SESSION MANAGEMENT
# ==========================================
def get_session(token):
    if len(sessions) > 100 and token not in sessions:
        try:
            sessions.pop(next(iter(sessions)), None)
        except (RuntimeError, StopIteration):
            pass

    if token not in sessions:
        sessions[token] = {
            "blood_context": {},
            "raw_text_chunks": [],
            "embeddings": [],
            "chat_history": []
        }
    return sessions[token]


# ==========================================
# 3. RAG ENGINE (Nomic Forced)
# ==========================================
def get_embedding(text):
    if not text: return []
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    if text_hash in embedding_cache:
        return embedding_cache[text_hash]

    try:
        r = requests.post(EMBED_ENDPOINT, json={
            "model": "nomic-embed-text",
            "prompt": text
        })
        vector = r.json().get('embedding')
        if vector:
            embedding_cache[text_hash] = vector
            return vector
    except Exception as e:
        logger.error(f"Embedding Error: {e}")
    return []


def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = sum(a * a for a in v1) ** 0.5
    mag2 = sum(b * b for b in v2) ** 0.5
    return dot / (mag1 * mag2) if mag1 * mag2 > 0 else 0


def retrieve_relevant_context(session, query, top_k=3):
    chunks = session.get('raw_text_chunks', [])
    embeddings = session.get('embeddings', [])
    if not chunks or not embeddings: return ""

    q_vec = get_embedding(query)
    if not q_vec: return ""

    scores = sorted([(cosine_similarity(q_vec, emb), chunk) for emb, chunk in zip(embeddings, chunks)],
                    key=lambda x: x[0], reverse=True)
    return "\n---\n".join([s[1] for s in scores[:top_k]])


# ==========================================
# 4. AGENT TOOLS
# ==========================================
def calculate_bmi(weight_kg, height_m):
    try:
        return f"BMI: {float(weight_kg) / (float(height_m) ** 2):.2f}"
    except:
        return "Error."


def estimate_daily_calories(weight_kg, activity_level="sedentary"):
    try:
        return f"TDEE: {int(10 * float(weight_kg) + 6.25 * 170 - 5 * 30 + 5)} kcal"
    except:
        return "Error."


AVAILABLE_TOOLS = {"calculate_bmi": calculate_bmi, "estimate_daily_calories": estimate_daily_calories}


def execute_tool_call(tool, args):
    if tool in AVAILABLE_TOOLS:
        try:
            return AVAILABLE_TOOLS[tool](**args)
        except:
            return "Tool Error"
    return "Unknown Tool"


# ==========================================
# 5. CORE AI ENGINE (The Fix)
# ==========================================
def clean_json_output(text):
    """
    STACK-BASED CLEANER: Finds the first valid JSON object or array
    and stops exactly when it closes. Ignores trailing text.
    Handles nested objects and strings correctly.
    """
    text = text.strip()

    # Locate the first possible start of JSON
    start_idx = -1
    for i, char in enumerate(text):
        if char in ['{', '[']:
            start_idx = i
            break

    if start_idx == -1: return text  # No JSON found

    # Stack counting
    stack = []
    in_string = False
    escape = False

    for i in range(start_idx, len(text)):
        char = text[i]

        if in_string:
            if char == '"' and not escape:
                in_string = False

            if char == '\\' and not escape:
                escape = True
            else:
                escape = False
        else:
            if char == '"':
                in_string = True
            elif char in ['{', '[']:
                stack.append(char)
            elif char in ['}', ']']:
                if not stack: break  # Error: unbalanced

                # Check for matching pair
                last = stack[-1]
                if (last == '{' and char == '}') or (last == '[' and char == ']'):
                    stack.pop()

                # If stack is empty, we found the full object!
                if not stack:
                    return text[start_idx: i + 1]

    return text[start_idx:]  # Fallback


def analyze_image(image_file, prompt):
    """
    Encodes image to base64 and sends to Ollama vision model.
    """
    try:
        # Reset file pointer if needed
        image_file.seek(0)
        img_bytes = image_file.read()
        b64_img = base64.b64encode(img_bytes).decode('utf-8')

        return query_ollama(prompt, images=[b64_img], temperature=0.2)
    except Exception as e:
        logger.error(f"Image Analysis Error: {e}")
        return None


def query_ollama(prompt, system_instruction=None, tools_enabled=False, temperature=0.1, retries=1, images=None):
    messages = []
    if system_instruction: messages.append({"role": "system", "content": system_instruction})

    user_msg = {"role": "user", "content": prompt}
    if images:
        user_msg["images"] = images
    messages.append(user_msg)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "format": "json",
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": 4096}
    }

    try:
        r = requests.post(CHAT_ENDPOINT, json=payload)
        response_text = r.json().get('message', {}).get('content', '')

        # Use the new robust cleaner
        cleaned = clean_json_output(response_text)

        data = json.loads(cleaned)

        # Tool Logic
        if tools_enabled and isinstance(data, dict) and "tool" in data:
            res = execute_tool_call(data["tool"], data.get("args", {}))
            return query_ollama(f"Tool Result: {res}. Answer user JSON.", system_instruction="Assistant",
                                tools_enabled=False)

        return data
    except json.JSONDecodeError:
        if retries > 0: return query_ollama(f"Fix JSON: {response_text}", retries=retries - 1)
        return None
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return None
