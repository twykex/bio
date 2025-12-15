import logging
import os
import re
import json
import uuid
import requests

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

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
sessions = {}

# --- HELPER FUNCTIONS ---

def get_session(token):
    # Basic memory management
    if len(sessions) > 100 and token not in sessions:
        # Remove oldest (insertion order preserved in Python 3.7+)
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
    """
    Advanced regex to fix common AI JSON mistakes.
    """
    # 1. Fix missing "title" key:
    # Looks for pattern: "day": "Mon", "Meal Name",
    # Replaces with: "day": "Mon", "title": "Meal Name",
    text = re.sub(r'("day":\s*"[^"]+",\s*)("[^"]+")(\s*,)', r'\1"title": \2\3', text)

    # 2. Fix missing "desc" or "benefit" keys if they appear as orphan strings
    text = re.sub(r'(,\s*)("[^"]+")(\s*\})', r'\1"desc": \2\3', text)

    return text


def fix_truncated_json(json_str):
    """Auto-completes JSON that was cut off."""
    json_str = json_str.strip()
    # Remove trailing comma if present
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
    """
    Safely removes // comments from JSON-like text, preserving strings.
    """
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
                # Comment detected. Skip until newline.
                i += 2
                while i < len(text) and text[i] != '\n':
                    i += 1
            else:
                output.append(char)
                i += 1
    return "".join(output)


def clean_and_parse_json(text):
    # 1. Strip Markdown
    text = text.replace("```json", "").replace("```", "")

    # 2. Try to find a complete JSON block first
    # This regex looks for { ... } or [ ... ] across lines.
    # It is greedy, so it finds the largest block.
    # Note: This works well if the noise is outside the JSON.
    match_complete = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)

    if match_complete:
        candidate = match_complete.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # If the "complete" block is invalid (e.g. syntax error inside),
            # we use it as the base for repairs.
            text = candidate
    else:
        # 3. If no complete block, extract from first { or [ to the end (handling truncation)
        match_start = re.search(r'(\{.*|\[.*)', text, re.DOTALL)
        if match_start:
            text = match_start.group(0)

    # 4. Apply Repairs
    text = repair_lazy_json(text)  # Fix missing keys
    text = re.sub(r'\]\s*"\s*\}', '] }', text)  # Fix rogue quotes
    text = re.sub(r',\s*\}', '}', text)  # Fix trailing commas
    text = re.sub(r',\s*\]', ']', text)

    text = remove_json_comments(text)

    # 5. Attempt Parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 6. Try fixing truncation
        logger.warning("JSON Invalid. Attempting auto-balance...")
        balanced_text = fix_truncated_json(text)
        try:
            return json.loads(balanced_text)
        except json.JSONDecodeError:
            return None


def query_ollama(prompt, retries=1):
    """
    Sends prompt to Ollama with retry logic.
    """
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


# --- ROUTES ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

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