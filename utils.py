import json
import re
import requests
import logging
import hashlib
import math
from functools import lru_cache
from config import OLLAMA_MODEL, OLLAMA_URL

logger = logging.getLogger(__name__)

# API Endpoints
CHAT_ENDPOINT = f"{OLLAMA_URL.rstrip('/')}/api/chat"
EMBED_ENDPOINT = f"{OLLAMA_URL.rstrip('/')}/api/embeddings"

# In-Memory Storage (Replace with Redis/DB in production)
sessions = {}
embedding_cache = {}


# ==========================================
# 1. SESSION MANAGEMENT
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
            "raw_text_chunks": [],  # For RAG
            "embeddings": [],  # For RAG
            "chat_history": []
        }
    return sessions[token]


# ==========================================
# 2. RAG ENGINE (Vector Math & Caching)
# ==========================================
def get_embedding(text):
    """Generates vector embedding with semantic caching."""
    # Create hash for cache key
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    if text_hash in embedding_cache:
        return embedding_cache[text_hash]

    try:
        r = requests.post(EMBED_ENDPOINT, json={"model": OLLAMA_MODEL, "prompt": text})
        vector = r.json().get('embedding')
        if vector:
            embedding_cache[text_hash] = vector  # Cache result
        return vector
    except Exception as e:
        logger.error(f"Embedding Error: {e}")
        return []


def cosine_similarity(v1, v2):
    """Math to find similarity between two vectors."""
    if not v1 or not v2: return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag_v1 = math.sqrt(sum(a * a for a in v1))
    mag_v2 = math.sqrt(sum(b * b for b in v2))
    if mag_v1 * mag_v2 == 0: return 0
    return dot_product / (mag_v1 * mag_v2)


def retrieve_relevant_context(session, query, top_k=3):
    """Finds PDF chunks relevant to the user's question."""
    chunks = session.get('raw_text_chunks', [])
    embeddings = session.get('embeddings', [])

    if not chunks or not embeddings: return ""

    query_vec = get_embedding(query)
    if not query_vec: return ""

    scores = []
    for i, emb in enumerate(embeddings):
        score = cosine_similarity(query_vec, emb)
        scores.append((score, chunks[i]))

    # Sort by relevance and return top K
    scores.sort(key=lambda x: x[0], reverse=True)
    return "\n---\n".join([item[1] for item in scores[:top_k]])


# ==========================================
# 3. AGENT TOOLS (Function Calling)
# ==========================================
def calculate_bmi(weight_kg, height_m):
    try:
        bmi = float(weight_kg) / (float(height_m) ** 2)
        return f"BMI Result: {bmi:.2f}"
    except:
        return "Error: Invalid input for BMI."


def estimate_daily_calories(weight_kg, activity_level="sedentary"):
    try:
        # Mifflin-St Jeor Equation (Simplified)
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
        logger.info(f"🛠️ AGENT CALL: {tool_name} {args}")
        try:
            return AVAILABLE_TOOLS[tool_name](**args)
        except Exception as e:
            return f"Tool Execution Failed: {e}"
    return "Tool not found."


# ==========================================
# 4. CORE AI ENGINE (Self-Healing)
# ==========================================
def clean_json_output(text):
    text = text.strip()
    text = re.sub(r'```(?:json)?', '', text).replace('```', '').strip()
    return text


def query_ollama(prompt, system_instruction=None, tools_enabled=False, temperature=0.2, retries=1):
    """
    Super-Advanced Query Function.
    Features: Tools, JSON Fixing, Temperature Control, Recursive Tool Execution.
    """
    messages = []

    # Inject Tool Definition if enabled
    if tools_enabled:
        tool_instr = """
        AVAILABLE TOOLS: ["calculate_bmi", "estimate_calories"].
        IF a calculation is needed, return strictly:
        { "tool": "calculate_bmi", "args": { "weight_kg": 70, "height_m": 1.8 } }
        OTHERWISE return:
        { "response": "Your answer here" }
        """
        system_instruction = (system_instruction or "") + "\n" + tool_instr

    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": temperature,
            "num_ctx": 4096,  # Long context window
            "top_p": 0.9
        }
    }

    try:
        r = requests.post(CHAT_ENDPOINT, json=payload)
        response_text = r.json().get('message', {}).get('content', '')
        cleaned_text = clean_json_output(response_text)
        data = json.loads(cleaned_text)

        # AGENT LOOP: Handle Tool Call
        if tools_enabled and "tool" in data:
            tool_res = execute_tool_call(data["tool"], data.get("args", {}))
            # RECURSIVE CALL: Feed tool result back to AI
            follow_up = f"TOOL RESULT: {tool_res}. Now give the final answer to the user."
            return query_ollama(follow_up, system_instruction="You are a helpful assistant.", tools_enabled=False)

        return data

    except json.JSONDecodeError as e:
        if retries > 0:
            logger.warning(f"⚠️ REPAIRING JSON: {e}")
            fix_prompt = f"Previous JSON was invalid: {response_text}. Error: {e}. Fix and return valid JSON."
            return query_ollama(fix_prompt, system_instruction="You are a JSON Syntax Repair Bot.", retries=retries - 1)
        return None
    except Exception as e:
        logger.error(f"Fatal AI Error: {e}")
        return None