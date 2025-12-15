### FILENAME: config.py ###
import os
import logging

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- CONFIGURATION ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2") # Standard model name
# CRITICAL FIX: Base URL only (removed /api/generate)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434") 
PORT = int(os.getenv("PORT", 5000))

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)