import os

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
PORT = int(os.getenv("PORT", 5000))
UPLOAD_FOLDER = 'uploads'
