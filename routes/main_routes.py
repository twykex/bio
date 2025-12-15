import os
import json
import logging
import pdfplumber
from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER
from utils import get_session, query_ollama

logger = logging.getLogger(__name__)

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/init_context', methods=['POST'])
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


@main_bp.route('/generate_week', methods=['POST'])
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


@main_bp.route('/chat_agent', methods=['POST'])
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


@main_bp.route('/get_recipe', methods=['POST'])
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


@main_bp.route('/generate_shopping_list', methods=['POST'])
def generate_shopping_list():
    data = request.json
    session = get_session(data.get('token'))
    prompt = f"""
    MEALS: {json.dumps(session.get('weekly_plan', []))}
    TASK: Shopping List JSON.
    FORMAT: {{ "Produce": ["A","B"], "Meat": ["C"], "Pantry": ["D"] }}
    """
    return jsonify(query_ollama(prompt) or {})


@main_bp.route('/generate_workout', methods=['POST'])
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


@main_bp.route('/explain_biomarker', methods=['POST'])
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
