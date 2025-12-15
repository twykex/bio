import json
import re
import requests
import logging
import base64
from config import OLLAMA_MODEL, OLLAMA_URL
from services.tools import execute_tool_call
from services.json_cleaner import (
    clean_json_output,
    repair_lazy_json,
    fix_truncated_json,
    remove_json_comments,
    clean_and_parse_json
)

logger = logging.getLogger(__name__)

base_url = OLLAMA_URL.replace("/api/generate", "").replace("/api/chat", "").rstrip("/")
CHAT_ENDPOINT = f"{base_url}/api/chat"

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
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})

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
        r = requests.post(CHAT_ENDPOINT, json=payload, timeout=60)

        if r.status_code != 200:
            logger.error(f"AI Error: API returned status code {r.status_code}: {r.text[:200]}")
            return None

        try:
            response_json = r.json()
        except ValueError:
             logger.error(f"AI Error: Invalid JSON response. Status: {r.status_code}, Body: {r.text[:200]}")
             return None

        response_text = response_json.get('message', {}).get('content', '')

        # Use the robust cleaner
        data = clean_and_parse_json(response_text)

        if data is None and retries > 0:
            logger.warning("🔄 JSON Failed. Retrying with stricter prompt...")
            prompt += "\nIMPORTANT: You previously outputted invalid JSON. Fix syntax. Ensure all keys are present."
            return query_ollama(prompt, system_instruction, tools_enabled, temperature, retries - 1, images)

        # Tool Logic
        if tools_enabled and isinstance(data, dict) and "tool" in data:
            res = execute_tool_call(data["tool"], data.get("args", {}))
            return query_ollama(f"Tool Result: {res}. Answer user JSON.", system_instruction="Assistant",
                                tools_enabled=False)

        return data
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return None
