import logging
from flask import Flask
from config import PORT, OLLAMA_MODEL
from routes.main_routes import main_bp
from routes.mini_apps import mini_apps_bp
# Exposing utilities for backward compatibility (e.g. tests)
from utils import get_session, repair_lazy_json, fix_truncated_json, clean_and_parse_json, query_ollama, remove_json_comments, sessions

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(mini_apps_bp)

if __name__ == '__main__':
    logger.info(f"🔋 HOSTING ON PORT {PORT} using model: {OLLAMA_MODEL}")
    app.run(debug=True, port=PORT)
