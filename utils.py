import json
import re
import requests
import logging
from config import OLLAMA_MODEL, OLLAMA_URL

logger = logging.getLogger(__name__)

sessions = {}

def get_session(token):
    # Basic memory management
    if len(sessions) > 100 and token not in sessions:
        # Remove oldest (insertion order preserved in Python 3.7+)
        try:
            sessions.pop(next(iter(sessions)), None)
        except (RuntimeError, StopIteration):
            pass

    if token not in sessions:
        sessions[token] = {
            "blood_context": {},
            "weekly_plan": [],
            "workout_plan": [],
            "chat_history": []
        }
    return sessions[token]


def repair_lazy_json(text):
    """
    Advanced regex to fix common AI JSON mistakes.
    """
    # 1. Fix missing "title" key:
    # Looks for pattern: "day": "Mon", "Meal Name",
    # Replaces with: "day": "Mon", "title": "Meal Name",
    text = re.sub(r'("day":\s*"[^"]+",\s*)("[^"]+")(\s*,)', r'\1"title": \2\3', text)

    # 2. Fix missing "desc" or "benefit" keys if they appear as orphan strings
    text = re.sub(r'(,\s*)("[^"]+")(\s*\})', r'\1"desc": \2\3', text)

    return text


def fix_truncated_json(json_str):
    """Auto-completes JSON that was cut off."""
    json_str = json_str.strip()
    # Remove trailing comma if present
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
    """
    Safely removes // comments from JSON-like text, preserving strings.
    """
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
                # Comment detected. Skip until newline.
                i += 2
                while i < len(text) and text[i] != '\n':
                    i += 1
            else:
                output.append(char)
                i += 1
    return "".join(output)


def clean_and_parse_json(text):
    # 1. Strip Markdown
    text = text.replace("```json", "").replace("```", "")

    # 2. Try to find a complete JSON block first
    # This regex looks for { ... } or [ ... ] across lines.
    # It is greedy, so it finds the largest block.
    # Note: This works well if the noise is outside the JSON.
    match_complete = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)

    if match_complete:
        candidate = match_complete.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # If the "complete" block is invalid (e.g. syntax error inside),
            # we use it as the base for repairs.
            text = candidate
    else:
        # 3. If no complete block, extract from first { or [ to the end (handling truncation)
        match_start = re.search(r'(\{.*|\[.*)', text, re.DOTALL)
        if match_start:
            text = match_start.group(0)

    # 4. Apply Repairs
    text = repair_lazy_json(text)  # Fix missing keys
    text = re.sub(r'\]\s*"\s*\}', '] }', text)  # Fix rogue quotes
    text = re.sub(r',\s*\}', '}', text)  # Fix trailing commas
    text = re.sub(r',\s*\]', ']', text)

    text = remove_json_comments(text)

    # 5. Attempt Parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 6. Try fixing truncation
        logger.warning("JSON Invalid. Attempting auto-balance...")
        balanced_text = fix_truncated_json(text)
        try:
            return json.loads(balanced_text)
        except json.JSONDecodeError:
            return None


def query_ollama(prompt, retries=1):
    """
    Sends prompt to Ollama with retry logic.
    """
    logger.info(f"🚀 SENDING PROMPT ({len(prompt)} chars)...")
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload)
        if r.status_code != 200: return None

        result = clean_and_parse_json(r.json().get('response', ''))

        if result is None and retries > 0:
            logger.warning("🔄 JSON Failed. Retrying with stricter prompt...")
            prompt += "\nIMPORTANT: You previously outputted invalid JSON. Fix syntax. Ensure all keys are present."
            return query_ollama(prompt, retries - 1)

        return result

    except Exception as e:
        logger.error(f"❌ CONNECTION ERROR: {e}")
        return None
