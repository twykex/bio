import requests
import logging
from config import OLLAMA_MODEL, OLLAMA_URL
from utils import clean_and_parse_json

logger = logging.getLogger(__name__)

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
