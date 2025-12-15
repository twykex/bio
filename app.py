import os
import logging
from flask import Flask

from config import PORT, OLLAMA_MODEL, UPLOAD_FOLDER
from routes.core import core_bp
from routes.features import features_bp

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.register_blueprint(core_bp)
app.register_blueprint(features_bp)

if __name__ == '__main__':
    logger.info(f"🔋 HOSTING ON PORT {PORT} using model: {OLLAMA_MODEL}")
    app.run(debug=True, port=PORT)
