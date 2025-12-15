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
from database import db

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

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# Register Blueprints
if main_bp:
    app.register_blueprint(main_bp)
if mini_apps_bp:
    app.register_blueprint(mini_apps_bp)

# --- DATA STORES ---
password_reset_tokens = {}

# --- HELPER FUNCTIONS ---

def get_session(token):
    if len(sessions) > 100 and token not in sessions:
        try:
            sessions.pop(next(iter(sessions)), None)
        except (RuntimeError, StopIteration):
            pass

    if token not in sessions:
        sessions[token] = {
            "blood_context": {},
            "weekly_plan": [],
            "workout_plan": [],
            "chat_history": []
        }
    return sessions[token]

def repair_lazy_json(text):
    text = re.sub(r'("day":\s*"[^"]+",\s*)("[^"]+")(\s*,)', r'\1"title": \2\3', text)
    text = re.sub(r'(,\s*)("[^"]+")(\s*\})', r'\1"desc": \2\3', text)
    return text

def fix_truncated_json(json_str):
    json_str = json_str.strip()
    json_str = re.sub(r',\s*$', '', json_str)
    stack = []
    is_inside_string = False
    escaped = False

    for char in json_str:
        if is_inside_string:
            if char == '"' and not escaped:
                is_inside_string = False
            elif char == '\\':
                escaped = not escaped
            else:
                escaped = False
        else:
            if char == '"':
                is_inside_string = True
            elif char == '{':
                stack.append('}')
            elif char == '[':
                stack.append(']')
            elif char == '}' or char == ']':
                if stack and stack[-1] == char:
                    stack.pop()

    if is_inside_string:
        json_str += '"'
    while stack:
        json_str += stack.pop()
    return json_str

def remove_json_comments(text):
    output = []
    in_string = False
    escape = False
    i = 0
    while i < len(text):
        char = text[i]
        if in_string:
            if char == '"' and not escape:
                in_string = False
            if char == '\\' and not escape:
                escape = True
            else:
                escape = False
            output.append(char)
            i += 1
        else:
            if char == '"':
                in_string = True
                output.append(char)
                i += 1
            elif char == '/' and i + 1 < len(text) and text[i+1] == '/':
                i += 2
                while i < len(text) and text[i] != '\n':
                    i += 1
            else:
                output.append(char)
                i += 1
    return "".join(output)

def clean_and_parse_json(text):
    text = text.replace("```json", "").replace("```", "")
    match_complete = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)

    if match_complete:
        candidate = match_complete.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            text = candidate
    else:
        match_start = re.search(r'(\{.*|\[.*)', text, re.DOTALL)
        if match_start:
            text = match_start.group(0)

    text = repair_lazy_json(text)
    text = re.sub(r'\]\s*"\s*\}', '] }', text)
    text = re.sub(r',\s*\}', '}', text)
    text = re.sub(r',\s*\]', ']', text)
    text = remove_json_comments(text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("JSON Invalid. Attempting auto-balance...")
        balanced_text = fix_truncated_json(text)
        try:
            return json.loads(balanced_text)
        except json.JSONDecodeError:
            return None

def query_ollama(prompt, retries=1):
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

        user = db.get_user_by_email(email)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
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

    # Check if we are upgrading a guest
    current_user_id = session.get('user_id')
    if current_user_id:
        current_user = db.get_user_by_id(current_user_id)
        if current_user and current_user['is_guest']:
            success, msg = db.convert_guest_to_user(current_user_id, email, generate_password_hash(password), name)
            if success:
                flash('Account created! Your guest data has been saved.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash(f'Error: {msg}', 'error')
                return redirect(url_for('login'))

    # New User
    existing_user = db.get_user_by_email(email)
    if existing_user:
        flash('Email already in use', 'error')
        return redirect(url_for('login'))

    user_id = db.create_user(email, generate_password_hash(password), name)
    if user_id:
        session['user_id'] = user_id
        return redirect(url_for('dashboard'))
    else:
        flash('Error creating account', 'error')
        return redirect(url_for('login'))

@app.route('/guest-login')
def guest_login():
    guest_id = db.create_user(None, None, "Guest", is_guest=True)
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
    user = db.get_user_by_email(email)
    if user:
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

        # Update password in DB
        db.update_password(email, generate_password_hash(password))

        password_reset_tokens.pop(token, None)
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = db.get_user_by_id(user_id)
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('login'))

    logger.info(f"Dashboard render: user_id={user_id}, is_guest={user['is_guest']}")
    return render_template('index.html', user_id=user_id, is_guest=bool(user['is_guest']), user_name=user['name'])

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