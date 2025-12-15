import logging
from flask import Flask, render_template
from config import PORT, OLLAMA_MODEL
from routes.main_routes import main_bp
from routes.mini_apps import mini_apps_bp

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(mini_apps_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    logger.info(f"🔋 HOSTING ON PORT {PORT} using model: {OLLAMA_MODEL}")
    app.run(debug=True, port=PORT)