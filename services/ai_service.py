import json
import re
import requests
import logging
import base64
from config import OLLAMA_MODEL, OLLAMA_URL
from services.tools import execute_tool_call

logger = logging.getLogger(__name__)

base_url = OLLAMA_URL.replace("/api/generate", "").replace("/api/chat", "").rstrip("/")
CHAT_ENDPOINT = f"{base_url}/api/chat"


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

    if start_idx == -1:
        return text  # No JSON found

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
                if not stack:
                    break  # Error: unbalanced

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


def repair_lazy_json(text):
    text = re.sub(r'("day":\s*"[^"]+",\s*)("[^"]+")(\s*,)', r'\1"title": \2\3', text)
    text = re.sub(r'(,\s*)("[^"]+")(\s*\})', r'\1"desc": \2\3', text)
    return text


def fix_truncated_json(json_str):
    json_str = json_str.strip()
    json_str = re.sub(r',\s*$', '', json_str)
    stack = []
    is_inside_string = False
    escaped = False

    for char in json_str:
        if is_inside_string:
            if char == '"' and not escaped:
                is_inside_string = False
            elif char == '\\':
                escaped = not escaped
            else:
                escaped = False
        else:
            if char == '"':
                is_inside_string = True
            elif char == '{':
                stack.append('}')
            elif char == '[':
                stack.append(']')
            elif char == '}' or char == ']':
                if stack and stack[-1] == char:
                    stack.pop()

    if is_inside_string:
        json_str += '"'
    while stack:
        json_str += stack.pop()
    return json_str


def remove_json_comments(text):
    output = []
    in_string = False
    escape = False
    i = 0
    while i < len(text):
        char = text[i]
        if in_string:
            if char == '"' and not escape:
                in_string = False
            if char == '\\' and not escape:
                escape = True
            else:
                escape = False
            output.append(char)
            i += 1
        else:
            if char == '"':
                in_string = True
                output.append(char)
                i += 1
            elif char == '/' and i + 1 < len(text) and text[i+1] == '/':
                i += 2
                while i < len(text) and text[i] != '\n':
                    i += 1
            else:
                output.append(char)
                i += 1
    return "".join(output)


def clean_and_parse_json(text):
    # 1. Use stack-based extractor to isolate JSON block
    cleaned = clean_json_output(text)

    # 2. Fix specific lazy patterns
    cleaned = repair_lazy_json(cleaned)
    cleaned = remove_json_comments(cleaned)

    # 3. Fix common syntax errors
    cleaned = re.sub(r'\]\s*"\s*\}', '] }', cleaned)
    cleaned = re.sub(r',\s*\}', '}', cleaned)
    cleaned = re.sub(r',\s*\]', ']', cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("JSON Invalid. Attempting auto-balance...")
        balanced = fix_truncated_json(cleaned)
        try:
            return json.loads(balanced)
        except json.JSONDecodeError:
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
        r = requests.post(CHAT_ENDPOINT, json=payload)
        response_text = r.json().get('message', {}).get('content', '')

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
