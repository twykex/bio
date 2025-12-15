### FILENAME: config.py ###
import os
import logging

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- CONFIGURATION ---
# CHANGED: Set to the specific model you want
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")

# CRITICAL: Point to the base URL (127.0.0.1 is safer than localhost on Windows)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

PORT = int(os.getenv("PORT", 5000))

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)