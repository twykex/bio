### FILENAME: utils.py ###
import json
import re
import requests
import logging
import hashlib
import math
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
        except:
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
# 3. RAG ENGINE (FIXED EMBEDDINGS)
# ==========================================
def get_embedding(text):
    """Generates vector embedding using NOMIC (Dedicated Embedding Model)."""
    if not text: return []

    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    if text_hash in embedding_cache:
        return embedding_cache[text_hash]

    try:
        # CRITICAL FIX: FORCE 'nomic-embed-text' FOR EMBEDDINGS
        # Gemma/Llama cannot do this efficiently.
        r = requests.post(EMBED_ENDPOINT, json={
            "model": "nomic-embed-text",
            "prompt": text
        })

        vector = r.json().get('embedding')
        if vector:
            embedding_cache[text_hash] = vector
        else:
            logger.warning(f"Embedding failed: {r.text}")

        return vector or []
    except Exception as e:
        logger.error(f"Embedding Error: {e}")
        return []


def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag_v1 = math.sqrt(sum(a * a for a in v1))
    mag_v2 = math.sqrt(sum(b * b for b in v2))
    if mag_v1 * mag_v2 == 0: return 0
    return dot_product / (mag_v1 * mag_v2)


def retrieve_relevant_context(session, query, top_k=3):
    chunks = session.get('raw_text_chunks', [])
    embeddings = session.get('embeddings', [])

    if not chunks or not embeddings: return ""

    query_vec = get_embedding(query)
    if not query_vec: return ""

    scores = []
    for i, emb in enumerate(embeddings):
        score = cosine_similarity(query_vec, emb)
        scores.append((score, chunks[i]))

    scores.sort(key=lambda x: x[0], reverse=True)
    return "\n---\n".join([item[1] for item in scores[:top_k]])


# ==========================================
# 4. AGENT TOOLS
# ==========================================
def calculate_bmi(weight_kg, height_m):
    try:
        bmi = float(weight_kg) / (float(height_m) ** 2)
        status = "Normal"
        if bmi < 18.5:
            status = "Underweight"
        elif bmi > 25:
            status = "Overweight"
        return f"BMI: {bmi:.2f} ({status})"
    except:
        return "Error: Invalid input."


def estimate_daily_calories(weight_kg, activity_level="sedentary"):
    try:
        base = 10 * float(weight_kg) + 6.25 * 170 - 5 * 30 + 5
        multipliers = {"sedentary": 1.2, "active": 1.55, "athlete": 1.7}
        val = base * multipliers.get(str(activity_level).lower(), 1.2)
        return f"Estimated TDEE: {val:.0f} kcal/day"
    except:
        return "Error calculating calories."


AVAILABLE_TOOLS = {
    "calculate_bmi": calculate_bmi,
    "estimate_calories": estimate_daily_calories
}


def execute_tool_call(tool_name, args):
    if tool_name in AVAILABLE_TOOLS:
        logger.info(f"🛠️ AGENT: {tool_name} {args}")
        try:
            return AVAILABLE_TOOLS[tool_name](**args)
        except Exception as e:
            return f"Tool Error: {e}"
    return "Tool not found."


# ==========================================
# 5. CORE AI ENGINE
# ==========================================
def clean_json_output(text):
    text = text.strip()
    text = re.sub(r'```(?:json)?', '', text).replace('```', '').strip()
    match_obj = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match_obj: return match_obj.group(0)
    return text


def query_ollama(prompt, system_instruction=None, tools_enabled=False, temperature=0.2, retries=1):
    messages = []
    if tools_enabled:
        system_instruction = (
                                         system_instruction or "") + "\nTOOLS: If calc needed, return JSON { \"tool\": \"calculate_bmi\", ... }"

    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature, "num_ctx": 4096}
    }

    try:
        r = requests.post(CHAT_ENDPOINT, json=payload)
        r.raise_for_status()

        response_text = r.json().get('message', {}).get('content', '')
        cleaned = clean_json_output(response_text)
        data = json.loads(cleaned)

        if tools_enabled and isinstance(data, dict) and "tool" in data:
            tool_res = execute_tool_call(data["tool"], data.get("args", {}))
            return query_ollama(f"TOOL RESULT: {tool_res}. Final answer JSON?", system_instruction="Helpful Assistant.",
                                tools_enabled=False)

        return data
    except json.JSONDecodeError:
        if retries > 0:
            return query_ollama(f"Fix invalid JSON: {response_text}", retries=retries - 1)
        return None
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return None