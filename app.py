import logging
import os
import uuid

from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Attempt to import config and blueprints from the main branch structure
# If these files don't exist yet in your feature branch, you may need to adjust paths
try:
    from config import PORT, OLLAMA_MODEL
except ImportError:
    # Fallback if config.py is missing
    PORT = int(os.getenv("PORT", 5000))
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

try:
    from routes.main_routes import main_bp
    from routes.mini_apps import mini_apps_bp
except ImportError:
    main_bp = None
    mini_apps_bp = None

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'super-secret-key-for-dev-only') # Use env var in production
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# Register Blueprints (from main branch)
if main_bp:
    app.register_blueprint(main_bp)
if mini_apps_bp:
    app.register_blueprint(mini_apps_bp)

# --- DATA STORES ---
# In-memory user store (for demonstration purposes only).
# In a production environment, this should be replaced with a proper database.
users = {}
password_reset_tokens = {}

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('landing.html', logged_in=('user_id' in session))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = users.get(email)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if email in users:
        flash('Email already in use', 'error')
        return redirect(url_for('login'))

    users[email] = {
        'name': name,
        'password': generate_password_hash(password)
    }
    session['user_id'] = email
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    if email in users:
        token = str(uuid.uuid4())
        password_reset_tokens[token] = email
        reset_link = url_for('reset_password', token=token, _external=True)
        logger.info(f"Password reset link for {email}: {reset_link}")
    return redirect(url_for('forgot_password_confirm'))

@app.route('/forgot-password-confirm')
def forgot_password_confirm():
    return render_template('forgot_password_confirm.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = password_reset_tokens.get(token)
    if not email:
        flash('Invalid or expired password reset link.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html')

        users[email]['password'] = generate_password_hash(password)
        password_reset_tokens.pop(token, None)
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

if __name__ == '__main__':
    logger.info(f"🔋 HOSTING ON PORT {PORT} using model: {OLLAMA_MODEL}")
    app.run(debug=True, port=PORT)
