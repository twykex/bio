import os
import json
import uuid
import re
import requests
import pdfplumber
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- CONFIGURATION ---
OLLAMA_MODEL = "huihui_ai/gemma3-abliterated:12b"
OLLAMA_URL = "http://localhost:11434/api/generate"

sessions = {}


def get_session(token):
    if token not in sessions:
        sessions[token] = {
            "blood_context": {},
            "weekly_plan": [],
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
    json_str = re.sub(r'[,"]+$', '', json_str)
    open_braces = json_str.count('{') - json_str.count('}')
    open_brackets = json_str.count('[') - json_str.count(']')
    if open_brackets > 0: json_str += ']' * open_brackets
    if open_braces > 0: json_str += '}' * open_braces
    return json_str


def clean_and_parse_json(text):
    # 1. Strip Markdown
    text = text.replace("```json", "").replace("```", "")

    # 2. Extract JSON block
    match = re.search(r'(\{.*|\[.*)', text, re.DOTALL)
    if match: text = match.group(0)

    # 3. Apply Repairs
    text = repair_lazy_json(text)  # Fix missing keys
    text = re.sub(r'\]\s*"\s*\}', '] }', text)  # Fix rogue quotes
    text = re.sub(r',\s*\}', '}', text)  # Fix trailing commas
    text = re.sub(r',\s*\]', ']', text)
    text = re.sub(r'//.*', '', text)  # Fix comments

    # 4. Attempt Parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 5. Try fixing truncation
        print("⚠️ JSON Invalid. Attempting auto-balance...")
        balanced_text = fix_truncated_json(text)
        try:
            return json.loads(balanced_text)
        except json.JSONDecodeError:
            return None


def query_ollama(prompt, retries=1):
    """
    Sends prompt to Ollama with retry logic.
    """
    print(f"\n🚀 SENDING PROMPT ({len(prompt)} chars)...")
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
            print("🔄 JSON Failed. Retrying with stricter prompt...")
            prompt += "\nIMPORTANT: You previously outputted invalid JSON. Fix syntax. Ensure all keys are present."
            return query_ollama(prompt, retries - 1)

        return result

    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return None


# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/init_context', methods=['POST'])
def init_context():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    token = request.form.get('token')

    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    text = ""
    try:
        with pdfplumber.open(os.path.join(UPLOAD_FOLDER, file.filename)) as pdf:
            for page in pdf.pages: text += (page.extract_text() or "") + "\n"
    except:
        return jsonify({"error": "PDF Error"}), 500

    print(f"📄 PDF LOADED: {len(text)} chars.")
    safe_text = text[:4500]

    prompt = f"""
    Role: Medical AI. Analyze this bloodwork.
    Task: Return JSON ONLY.
    Structure:
    {{ 
        "summary": "Short summary", 
        "strategies": [
            {{ "name": "Vitamin D", "desc": "Optimize levels" }},
            {{ "name": "Metabolic", "desc": "Insulin control" }},
            {{ "name": "Inflammation", "desc": "Reduce stress" }}
        ] 
    }}
    DATA: {safe_text}
    """

    data = query_ollama(prompt)
    if not data:
        # Emergency Fallback
        data = {
            "summary": "Analysis failed, but strategies loaded.",
            "strategies": [{"name": "General Health", "desc": "Balanced approach."}]
        }

    session = get_session(token)
    session["blood_context"] = data
    return jsonify(data)


@app.route('/generate_week', methods=['POST'])
def generate_week():
    data = request.json
    session = get_session(data.get('token'))
    strategy = data.get('strategy_name')

    print(f"📅 GENERATING PLAN: {strategy}")

    prompt = f"""
    CONTEXT: {json.dumps(session.get('blood_context', {}))}
    STRATEGY: {strategy}
    TASK: 7-Day Dinner Plan.
    OUTPUT: JSON Array of 7 objects.
    FORMAT:
    [
        {{ "day": "Mon", "title": "Salmon", "ingredients": ["Fish","Rice"], "benefit": "Omega3" }},
        {{ "day": "Tue", "title": "Chicken", "ingredients": ["Meat","Veg"], "benefit": "Protein" }}
        ...
    ]
    """

    plan = query_ollama(prompt)

    if not plan:
        print("❌ AI Failed. Serving Fallback Plan.")
        # Fallback Plan so UI never breaks
        plan = [
            {"day": "Mon", "title": "Grilled Salmon", "ingredients": ["Salmon", "Asparagus"],
             "benefit": "Fallback Meal"},
            {"day": "Tue", "title": "Chicken Breast", "ingredients": ["Chicken", "Broccoli"],
             "benefit": "Fallback Meal"},
            {"day": "Wed", "title": "Beef Stir Fry", "ingredients": ["Beef", "Peppers"], "benefit": "Fallback Meal"},
            {"day": "Thu", "title": "Turkey Bowl", "ingredients": ["Turkey", "Rice"], "benefit": "Fallback Meal"},
            {"day": "Fri", "title": "White Fish", "ingredients": ["Cod", "Green Beans"], "benefit": "Fallback Meal"},
            {"day": "Sat", "title": "Steak Salad", "ingredients": ["Steak", "Greens"], "benefit": "Fallback Meal"},
            {"day": "Sun", "title": "Roast Chicken", "ingredients": ["Chicken", "Potatoes"], "benefit": "Fallback Meal"}
        ]

    session["weekly_plan"] = plan
    return jsonify(plan)


@app.route('/chat_agent', methods=['POST'])
def chat_agent():
    data = request.json
    session = get_session(data.get('token'))
    prompt = f"""
    DATA: {str(session.get('weekly_plan', []))[:500]}
    USER: "{data.get('message')}"
    RESPONSE FORMAT JSON: {{ "response": "Answer here" }}
    """
    resp = query_ollama(prompt)
    return jsonify(resp if resp else {"response": "I'm having trouble connecting to your data."})


@app.route('/get_recipe', methods=['POST'])
def get_recipe():
    data = request.json
    prompt = f"""
    Recipe for "{data.get('meal_title')}".
    FORMAT JSON:
    {{
        "prep_time": "15m", 
        "steps": ["Step 1", "Step 2"],
        "macros": {{ "protein": "30g", "carbs": "20g", "fats": "15g" }},
        "tips": "Tip here"
    }}
    """
    return jsonify(query_ollama(prompt) or {})


@app.route('/generate_shopping_list', methods=['POST'])
def generate_shopping_list():
    data = request.json
    session = get_session(data.get('token'))
    prompt = f"""
    MEALS: {json.dumps(session.get('weekly_plan', []))}
    TASK: Shopping List JSON.
    FORMAT: {{ "Produce": ["A","B"], "Meat": ["C"], "Pantry": ["D"] }}
    """
    return jsonify(query_ollama(prompt) or {})


if __name__ == '__main__':
    print(f"🔋 HOSTING ON PORT 5000 using model: {OLLAMA_MODEL}")
    app.run(debug=True, port=5000)