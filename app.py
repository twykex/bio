import os
import json
import uuid
import re
import requests
import pdfplumber
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- CONFIGURATION ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
PORT = int(os.getenv("PORT", 5000))

sessions = {}

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
    return render_template('index.html')


@app.route('/init_context', methods=['POST'])
def init_context():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    token = request.form.get('token')

    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file type. Only PDF allowed."}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages: text += (page.extract_text() or "") + "\n"
    except Exception as e:
        logger.error(f"Failed to parse PDF: {e}")
        return jsonify({"error": "PDF Parsing Error"}), 500

    logger.info(f"📄 PDF LOADED: {len(text)} chars.")
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
        logger.warning("Using fallback analysis strategy.")
        data = {
            "summary": "Analysis failed, but strategies loaded.",
            "strategies": [
                {"name": "General Health", "desc": "Balanced approach."},
                {"name": "Muscle Gain", "desc": "High protein, hypertrophy focus."},
                {"name": "Weight Loss", "desc": "Caloric deficit, high volume foods."}
            ]
        }

    session = get_session(token)
    session["blood_context"] = data
    return jsonify(data)


@app.route('/generate_week', methods=['POST'])
def generate_week():
    data = request.json
    session = get_session(data.get('token'))
    strategy = data.get('strategy_name')
    preferences = data.get('preferences', 'None')

    logger.info(f"📅 GENERATING PLAN: {strategy} (Prefs: {preferences})")

    prompt = f"""
    CONTEXT: {json.dumps(session.get('blood_context', {}))}
    STRATEGY: {strategy}
    PREFERENCES: {preferences}
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
        logger.error("AI Failed. Serving Fallback Plan.")
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
    user_msg = data.get('message')

    # Update History
    history = session.get('chat_history', [])
    history.append({"role": "user", "text": user_msg})

    # Context window management (last 10 messages)
    recent_history = history[-10:]

    prompt = f"""
    DATA: {str(session.get('weekly_plan', []))[:500]}
    HISTORY: {json.dumps(recent_history)}
    USER: "{user_msg}"
    RESPONSE FORMAT JSON: {{ "response": "Answer here" }}
    """
    resp = query_ollama(prompt)

    if resp and 'response' in resp:
        history.append({"role": "ai", "text": resp['response']})

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


@app.route('/generate_workout', methods=['POST'])
def generate_workout():
    data = request.json
    session = get_session(data.get('token'))
    strategy = data.get('strategy_name') or "General Health"

    logger.info(f"🏋️ GENERATING WORKOUT: {strategy}")

    prompt = f"""
    CONTEXT: {json.dumps(session.get('blood_context', {}))}
    STRATEGY: {strategy}
    TASK: 7-Day Workout Plan.
    OUTPUT: JSON Array of 7 objects.
    FORMAT:
    [
        {{ "day": "Mon", "focus": "Cardio", "exercises": ["Run 30m", "Stretch"], "benefit": "Heart Health" }},
        {{ "day": "Tue", "focus": "Strength", "exercises": ["Squats", "Pushups"], "benefit": "Muscle" }}
    ]
    """

    plan = query_ollama(prompt)

    if not plan:
        plan = [
            {"day": "Mon", "focus": "Light Cardio", "exercises": ["30m Walk"], "benefit": "Circulation"},
            {"day": "Tue", "focus": "Rest", "exercises": ["Stretching"], "benefit": "Recovery"},
            {"day": "Wed", "focus": "Bodyweight", "exercises": ["Squats", "Pushups"], "benefit": "Strength"},
            {"day": "Thu", "focus": "Mobility", "exercises": ["Yoga Flow"], "benefit": "Flexibility"},
            {"day": "Fri", "focus": "Cardio", "exercises": ["Jogging"], "benefit": "Endurance"},
            {"day": "Sat", "focus": "Active Rest", "exercises": ["Hiking"], "benefit": "Mental Health"},
            {"day": "Sun", "focus": "Rest", "exercises": ["None"], "benefit": "Recovery"}
        ]

    session["workout_plan"] = plan
    return jsonify(plan)


@app.route('/explain_biomarker', methods=['POST'])
def explain_biomarker():
    data = request.json
    session = get_session(data.get('token'))
    biomarker = data.get('biomarker')

    prompt = f"""
    CONTEXT: {json.dumps(session.get('blood_context', {}))}
    BIOMARKER: {biomarker}
    TASK: Explain this biomarker in the context of the user's health data.
    OUTPUT: JSON with keys "explanation" and "recommendation".
    FORMAT: {{ "explanation": "...", "recommendation": "..." }}
    """
    return jsonify(query_ollama(prompt) or {"explanation": "Could not analyze.", "recommendation": "Consult a doctor."})


# --- 20 MINI OLLAMA FEATURES ---

@app.route('/suggest_supplement', methods=['POST'])
def suggest_supplement():
    data = request.json
    focus = data.get('focus', 'general health')
    prompt = f"Suggest 3 supplements for {focus}. Output JSON: {{ 'supplements': [{{ 'name': '...', 'reason': '...' }}] }}"
    return jsonify(query_ollama(prompt) or {
        "supplements": [
            {"name": "Vitamin D", "reason": "General immune support and mood regulation"},
            {"name": "Magnesium", "reason": "Supports muscle recovery and sleep quality"},
            {"name": "Omega-3", "reason": "Reduces inflammation and supports heart health"}
        ]
    })

@app.route('/check_food_interaction', methods=['POST'])
def check_food_interaction():
    data = request.json
    item1 = data.get('item1', '')
    item2 = data.get('item2', '')
    prompt = f"Check interaction between {item1} and {item2}. Output JSON: {{ 'interaction': 'Safe/Caution/Danger', 'details': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "interaction": "Caution (Fallback)",
        "details": "Could not verify interaction safely. Please consult a medical professional before combining."
    })

@app.route('/recipe_variation', methods=['POST'])
def recipe_variation():
    data = request.json
    recipe = data.get('recipe', 'the dish')
    variation_type = data.get('type', 'healthy')
    prompt = f"Create a {variation_type} variation of {recipe}. Output JSON: {{ 'recipe': '...', 'changes': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "recipe": f"{variation_type} {recipe}",
        "changes": "Substituted heavy ingredients for lighter alternatives. Adjusted cooking method to retain nutrients."
    })

@app.route('/flavor_pairing', methods=['POST'])
def flavor_pairing():
    data = request.json
    ingredient = data.get('ingredient', '')
    prompt = f"Suggest 3 spices or flavors that pair well with {ingredient}. Output JSON: {{ 'pairings': ['...', '...', '...'] }}"
    return jsonify(query_ollama(prompt) or {
        "pairings": ["Garlic", "Lemon Zest", "Thyme"]
    })

@app.route('/quick_snack', methods=['POST'])
def quick_snack():
    data = request.json
    preference = data.get('preference', 'healthy')
    prompt = f"Suggest a quick snack involving {preference}. Output JSON: {{ 'snack': '...', 'calories': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "snack": "Apple slices with Almond Butter",
        "calories": "~200 kcal"
    })

@app.route('/hydration_tip', methods=['POST'])
def hydration_tip():
    data = request.json
    activity = data.get('activity', 'sedentary')
    prompt = f"Give a hydration tip for someone who is {activity}. Output JSON: {{ 'tip': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "tip": "Aim to drink at least 8 glasses (2 liters) of water daily. Increase intake if active or in hot weather."
    })

@app.route('/mood_food', methods=['POST'])
def mood_food():
    data = request.json
    mood = data.get('mood', 'neutral')
    prompt = f"Suggest a food that helps with {mood} mood. Output JSON: {{ 'food': '...', 'why': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "food": "Dark Chocolate (>70%)",
        "why": "Contains compounds that may improve mood and reduce stress hormones."
    })

@app.route('/energy_booster', methods=['POST'])
def energy_booster():
    data = request.json
    context = data.get('context', 'general')
    prompt = f"Suggest a natural energy boosting food for {context}. Output JSON: {{ 'food': '...', 'benefit': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "food": "Banana",
        "benefit": "Rich in potassium and natural sugars for a quick, sustained energy boost."
    })

@app.route('/recovery_meal', methods=['POST'])
def recovery_meal():
    data = request.json
    workout = data.get('workout', 'general')
    prompt = f"Suggest a post-workout recovery meal for {workout}. Output JSON: {{ 'meal': '...', 'nutrients': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "meal": "Grilled Chicken with Quinoa and Avocado",
        "nutrients": "High protein for muscle repair, complex carbs for glycogen replenishment, and healthy fats."
    })

@app.route('/sleep_aid', methods=['POST'])
def sleep_aid():
    data = request.json
    issue = data.get('issue', 'general')
    prompt = f"Suggest a food or drink to help sleep for {issue}. Output JSON: {{ 'recommendation': '...', 'mechanism': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "recommendation": "Chamomile Tea or Warm Milk",
        "mechanism": "Contains compounds like apigenin or tryptophan that promote relaxation and better sleep."
    })

@app.route('/digestive_aid', methods=['POST'])
def digestive_aid():
    data = request.json
    symptom = data.get('symptom', 'general')
    prompt = f"Suggest a food to help with {symptom} digestion. Output JSON: {{ 'food': '...', 'benefit': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "food": "Ginger Tea",
        "benefit": "Known to alleviate nausea and settle the stomach."
    })

@app.route('/immunity_booster', methods=['POST'])
def immunity_booster():
    data = request.json
    season = data.get('season', 'general')
    prompt = f"Suggest immunity-boosting foods for {season}. Output JSON: {{ 'foods': ['...', '...'] }}"
    return jsonify(query_ollama(prompt) or {
        "foods": ["Citrus Fruits (Vitamin C)", "Garlic", "Ginger", "Spinach"]
    })

@app.route('/anti_inflammatory', methods=['POST'])
def anti_inflammatory():
    data = request.json
    condition = data.get('condition', 'general')
    prompt = f"Suggest anti-inflammatory foods for {condition}. Output JSON: {{ 'foods': ['...', '...'] }}"
    return jsonify(query_ollama(prompt) or {
        "foods": ["Fatty Fish (Salmon)", "Berries", "Turmeric", "Green Tea"]
    })

@app.route('/antioxidant_rich', methods=['POST'])
def antioxidant_rich():
    data = request.json
    preference = data.get('preference', 'any')
    prompt = f"Suggest antioxidant-rich foods, preference: {preference}. Output JSON: {{ 'foods': ['...', '...'] }}"
    return jsonify(query_ollama(prompt) or {
        "foods": ["Blueberries", "Dark Chocolate", "Pecans", "Artichokes"]
    })

@app.route('/low_gi_option', methods=['POST'])
def low_gi_option():
    data = request.json
    food = data.get('food', 'high GI food')
    prompt = f"Suggest a low GI alternative to {food}. Output JSON: {{ 'alternative': '...', 'gi_diff': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "alternative": "Quinoa or Brown Rice",
        "gi_diff": "Significantly lower Glycemic Index, providing more stable blood sugar levels."
    })

@app.route('/high_protein_option', methods=['POST'])
def high_protein_option():
    data = request.json
    food = data.get('food', 'food')
    prompt = f"Suggest a high protein alternative to {food}. Output JSON: {{ 'alternative': '...', 'protein_content': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "alternative": "Greek Yogurt or Chicken Breast",
        "protein_content": "Contains significantly more protein per serving."
    })

@app.route('/fiber_rich_option', methods=['POST'])
def fiber_rich_option():
    data = request.json
    food = data.get('food', 'food')
    prompt = f"Suggest a fiber rich alternative to {food}. Output JSON: {{ 'alternative': '...', 'fiber_content': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "alternative": "Lentils or Chia Seeds",
        "fiber_content": "High fiber content promotes digestive health."
    })

@app.route('/seasonal_swap', methods=['POST'])
def seasonal_swap():
    data = request.json
    ingredient = data.get('ingredient', 'ingredient')
    season = data.get('season', 'current')
    prompt = f"Suggest a seasonal alternative to {ingredient} for {season}. Output JSON: {{ 'swap': '...', 'reason': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "swap": "Frozen or Canned Alternative",
        "reason": "When out of season, frozen options often retain more nutrients than imported fresh produce."
    })

@app.route('/budget_swap', methods=['POST'])
def budget_swap():
    data = request.json
    ingredient = data.get('ingredient', 'expensive ingredient')
    prompt = f"Suggest a cheaper alternative to {ingredient}. Output JSON: {{ 'swap': '...', 'savings': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "swap": "Beans, Lentils, or Seasonal Produce",
        "savings": "Cost-effective staples that provide similar nutritional value."
    })

@app.route('/leftover_idea', methods=['POST'])
def leftover_idea():
    data = request.json
    food = data.get('food', 'leftovers')
    prompt = f"Suggest a creative way to use leftover {food}. Output JSON: {{ 'idea': '...', 'recipe_hint': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "idea": "Hearty Stir-Fry or Salad",
        "recipe_hint": "Toss with fresh vegetables and a light dressing or soy sauce."
    })


@app.route('/stress_relief', methods=['POST'])
def stress_relief():
    data = request.json
    context = data.get('context', 'general')
    prompt = f"Suggest a stress relief technique for {context}. Output JSON: {{ 'technique': '...', 'steps': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "technique": "Box Breathing",
        "steps": "Inhale for 4s, hold for 4s, exhale for 4s, hold for 4s. Repeat 4 times."
    })


@app.route('/focus_technique', methods=['POST'])
def focus_technique():
    data = request.json
    task = data.get('task', 'general work')
    prompt = f"Suggest a focus technique for {task}. Output JSON: {{ 'technique': '...', 'description': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "technique": "Pomodoro Technique",
        "description": "Work for 25 minutes, then take a 5-minute break. Repeat."
    })


@app.route('/exercise_alternative', methods=['POST'])
def exercise_alternative():
    data = request.json
    exercise = data.get('exercise', 'running')
    reason = data.get('reason', 'injury')
    prompt = f"Suggest an alternative to {exercise} due to {reason}. Output JSON: {{ 'alternative': '...', 'benefit': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "alternative": "Swimming",
        "benefit": "Low impact cardio that protects joints while building endurance."
    })


if __name__ == '__main__':
    logger.info(f"🔋 HOSTING ON PORT {PORT} using model: {OLLAMA_MODEL}")
    app.run(debug=True, port=PORT)
