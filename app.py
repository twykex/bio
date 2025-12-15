import logging
import os
import re
import json
import uuid
import requests
import socket
import webbrowser
import threading
from time import sleep

from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Attempt to import config and blueprints from the main branch structure
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
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'super-secret-key-for-dev-only')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register Blueprints
if main_bp:
    app.register_blueprint(main_bp)
if mini_apps_bp:
    app.register_blueprint(mini_apps_bp)

# --- DATA STORES ---
users = {}
password_reset_tokens = {}

# --- NEW UTILITIES: Port Finding & Browser Opening ---

def find_free_port(start_port):
    port = start_port
    while port < start_port + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            if result != 0:
                return port
            else:
                port += 1
    return start_port

def open_browser(port):
    sleep(1.5) 
    url = f"http://127.0.0.1:{port}"
    logger.info(f"🌍 Opening browser at {url}...")
    try:
        browser = webbrowser.get('chrome')
    except webbrowser.Error:
        try:
            browser = webbrowser.get('open -a /Applications/Google\ Chrome.app %s')
        except webbrowser.Error:
            browser = webbrowser
    browser.open(url)

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

@app.route('/guest-login')
def guest_login():
    guest_id = f"guest_{uuid.uuid4()}"
    session['user_id'] = guest_id
    logger.info(f"Guest login: {guest_id}")
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