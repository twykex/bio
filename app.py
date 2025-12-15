import logging
import os
import threading

from flask import Flask, render_template, session, redirect, url_for

# Attempt to import config and blueprints from the main branch structure
try:
    from config import PORT, OLLAMA_MODEL
except ImportError:
    # Fallback if config.py is missing
    PORT = int(os.getenv("PORT", 5000))
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

try:
    from routes.meal_routes import meal_bp
    from routes.workout_routes import workout_bp
    from routes.health_routes import health_bp
    from routes.mini_apps import mini_apps_bp
    from routes.auth_routes import auth_bp
except ImportError:
    meal_bp = None
    workout_bp = None
    health_bp = None
    mini_apps_bp = None
    auth_bp = None

from server_utils import find_free_port, open_browser

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'super-secret-key-for-dev-only')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register Blueprints
if meal_bp:
    app.register_blueprint(meal_bp)
if workout_bp:
    app.register_blueprint(workout_bp)
if health_bp:
    app.register_blueprint(health_bp)
if mini_apps_bp:
    app.register_blueprint(mini_apps_bp)
if auth_bp:
    app.register_blueprint(auth_bp)

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('landing.html', logged_in=('user_id' in session))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user_id=session['user_id'])


if __name__ == '__main__':
    # Fix for double-execution of port finding in Flask Debug mode
    if os.environ.get('SERVER_PORT'):
        actual_port = int(os.environ.get('SERVER_PORT'))
    else:
        actual_port = find_free_port(PORT)
        os.environ['SERVER_PORT'] = str(actual_port)
        if actual_port != PORT:
            logger.warning(f"⚠️  Port {PORT} is in use. Switched to {actual_port}.")

    logger.info(f"🔋 HOSTING ON PORT {actual_port} using model: {OLLAMA_MODEL}")

    # Open browser only in the reloader process
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=open_browser, args=(actual_port,)).start()

    app.run(debug=True, port=actual_port)
