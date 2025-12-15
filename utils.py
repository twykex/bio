import json
import re
import requests
import logging
from config import OLLAMA_MODEL, OLLAMA_URL

logger = logging.getLogger(__name__)

# Ensure we are using the chat endpoint for advanced context
# If OLLAMA_URL is "http://localhost:11434", this appends the chat path
CHAT_ENDPOINT = f"{OLLAMA_URL.rstrip('/')}/api/chat"

sessions = {}


def get_session(token):
    """
    In-memory session management.
    (In production, replace this with Redis).
    """
    if len(sessions) > 100 and token not in sessions:
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


def clean_json_output(text):
    """
    Cleans text to ensure valid JSON.
    Even with format='json', models sometimes wrap output in Markdown.
    """
    text = text.strip()

    # 1. Remove Markdown Code Blocks
    match = re.search(r'```(?:json)?\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
    if match:
        text = match.group(1)

    # 2. If it's not wrapped in code blocks, look for the first { or [
    else:
        match_start = re.search(r'(\{.*|\[.*)', text, re.DOTALL)
        if match_start:
            text = match_start.group(0)

    # 3. Handle Truncation (Auto-close brackets if model runs out of tokens)
    # Simple stack balancer
    stack = []
    is_string = False
    for char in text:
        if char == '"' and (not stack or stack[-1] != '\\'):
            is_string = not is_string
        if not is_string:
            if char == '{':
                stack.append('}')
            elif char == '[':
                stack.append(']')
            elif char == '}' or char == ']':
                if stack: stack.pop()

    # If stack is not empty, append missing closing brackets
    if stack:
        text += "".join(reversed(stack))

    return text


def query_ollama(prompt, system_instruction=None, model=OLLAMA_MODEL, temperature=0.3):
    """
    Advanced Query Function.
    - Uses /api/chat for Role-based prompting.
    - Enforces JSON format.
    - Handles retry logic internally.
    """

    messages = []

    # 1. Add System Instruction (The Persona/Rules)
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    else:
        # Default system instruction to ensure JSON
        messages.append({"role": "system", "content": "You are a helpful medical AI. You strictly output valid JSON."})

    # 2. Add User Prompt (The Data/Task)
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "format": "json",  # FORCE JSON MODE (Ollama Feature)
        "options": {
            "temperature": temperature,  # Low temp = more deterministic/analytical
            "num_ctx": 4096,  # 4k context window to fit PDF data
            "top_p": 0.9
        }
    }

    logger.info(f"🚀 SENDING AI REQUEST: {len(prompt)} chars | System: {bool(system_instruction)}")

    try:
        r = requests.post(CHAT_ENDPOINT, json=payload)
        r.raise_for_status()

        response_json = r.json()
        content = response_json.get('message', {}).get('content', '')

        # Attempt clean parse
        cleaned_text = clean_json_output(content)

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON PARSE FAIL: {e}")
            logger.debug(f"Bad Content: {content}")
            return None

    except Exception as e:
        logger.error(f"❌ CONNECTION ERROR: {e}")
        return None