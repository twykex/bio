### FILENAME: main_routes.py ###
import os
import json
import logging
import pdfplumber
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER
from utils import get_session, query_ollama, get_embedding, retrieve_relevant_context

logger = logging.getLogger(__name__)
main_bp = Blueprint('main_bp', __name__)

# --- FALLBACK DATA ---
FALLBACK_MEAL_PLAN = [
    {"day": "Mon", "title": "Grilled Salmon Bowl", "ingredients": ["Salmon", "Quinoa", "Avocado"],
     "benefit": "High Omega-3s."},
    {"day": "Tue", "title": "Chicken Stir-Fry", "ingredients": ["Chicken", "Broccoli", "Ginger"],
     "benefit": "Lean protein."},
    {"day": "Wed", "title": "Turkey Chili", "ingredients": ["Turkey", "Beans", "Tomatoes"], "benefit": "High Fiber."},
    {"day": "Thu", "title": "Beef & Asparagus", "ingredients": ["Beef", "Asparagus", "Garlic"],
     "benefit": "Iron boost."},
    {"day": "Fri", "title": "White Fish Tacos", "ingredients": ["Cod", "Corn Tortillas", "Slaw"],
     "benefit": "Light protein."},
    {"day": "Sat", "title": "Mediterranean Salad", "ingredients": ["Chickpeas", "Feta", "Cucumber"],
     "benefit": "Antioxidants."},
    {"day": "Sun", "title": "Roast Chicken", "ingredients": ["Chicken", "Sweet Potato", "Carrots"],
     "benefit": "Complex carbs."}
]

FALLBACK_WORKOUT_PLAN = [
    {"day": "Mon", "focus": "Cardio", "exercises": ["30m Jog"], "benefit": "Heart Health"},
    {"day": "Tue", "focus": "Upper Body", "exercises": ["Pushups", "Rows"], "benefit": "Strength"},
    {"day": "Wed", "focus": "Active Rest", "exercises": ["Yoga"], "benefit": "Recovery"},
    {"day": "Thu", "focus": "Lower Body", "exercises": ["Squats", "Lunges"], "benefit": "Leg Power"},
    {"day": "Fri", "focus": "HIIT", "exercises": ["Burpees", "Sprints"], "benefit": "Fat Loss"},
    {"day": "Sat", "focus": "Outdoors", "exercises": ["Hiking"], "benefit": "Mental Health"},
    {"day": "Sun", "focus": "Rest", "exercises": ["None"], "benefit": "Recovery"}
]


def advanced_pdf_parse(filepath):
    """Extracts text and splits it into logical chunks for RAG."""
    full_text = ""
    chunks = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                full_text += text + "\n"
                page_chunks = [c.strip() for c in text.split('\n\n') if len(c) > 50]
                chunks.extend(page_chunks)
    except Exception as e:
        logger.error(f"PDF Error: {e}")
    return full_text, chunks


@main_bp.route('/init_context', methods=['POST'])
def init_context():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    token = request.form.get('token')

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    text, chunks = advanced_pdf_parse(filepath)
    safe_chunks = chunks[:50]

    embeddings = [get_embedding(chunk) for chunk in safe_chunks]

    session = get_session(token)
    session['raw_text_chunks'] = safe_chunks
    session['embeddings'] = embeddings

    # OPTIMIZED PROMPT FOR SMALL MODELS
    system_prompt = "You are a Medical AI. Return strict JSON only. No markdown."
    user_prompt = f"""
    DATA: {text[:6000]}

    TASK: Analyze health data.
    OUTPUT JSON FORMAT:
    {{
        "summary": "2 sentences on health status.",
        "strategies": [
            {{ "name": "Metabolic Reset", "desc": "Optimize insulin." }},
            {{ "name": "Anti-Inflammatory", "desc": "Reduce inflammation." }}
        ]
    }}
    """

    data = query_ollama(user_prompt, system_instruction=system_prompt, temperature=0.1)

    if not data:
        data = {
            "summary": "Analysis complete. Optimization recommended.",
            "strategies": [
                {"name": "Metabolic Reset", "desc": "Optimize insulin sensitivity."},
                {"name": "Anti-Inflammatory", "desc": "Reduce systemic inflammation."},
                {"name": "Hormonal Balance", "desc": "Support thyroid and adrenal health."}
            ]
        }

    session["blood_context"] = data
    return jsonify(data)


@main_bp.route('/generate_week', methods=['POST'])
def generate_week():
    data = request.json
    session = get_session(data.get('token'))
    strategy = data.get('strategy_name', 'General')
    preferences = data.get('preferences', 'None')

    logger.info(f"📅 Generating Meal Plan for: {strategy}")

    # OPTIMIZED PROMPT: ONE-SHOT LEARNING
    # We give it an exact example to copy. This helps small models drastically.
    prompt = f"""
    Role: Nutritionist. Strategy: {strategy}. Preferences: {preferences}.
    Task: 7-Day Dinner Plan.
    Output: STRICT JSON ONLY.

    EXAMPLE JSON STRUCTURE:
    [
      {{ "day": "Mon", "title": "Salmon Bowl", "ingredients": ["Salmon", "Rice"], "benefit": "Omega-3" }},
      {{ "day": "Tue", "title": "Chicken Salad", "ingredients": ["Chicken", "Greens"], "benefit": "Protein" }}
    ]

    GENERATE 7 DAYS NOW:
    """

    plan = query_ollama(prompt, system_instruction="Return JSON Array only.", temperature=0.3)

    if isinstance(plan, dict) and 'plan' in plan: plan = plan['plan']

    if not plan or not isinstance(plan, list) or len(plan) == 0:
        logger.warning("❌ AI MEAL PLAN FAILED. Using Fallback.")
        plan = FALLBACK_MEAL_PLAN

    return jsonify(plan)


@main_bp.route('/generate_workout', methods=['POST'])
def generate_workout():
    data = request.json
    session = get_session(data.get('token'))
    strategy = data.get('strategy_name', 'General')

    logger.info(f"💪 Generating Workout for: {strategy}")

    prompt = f"""
    Role: Trainer. Strategy: {strategy}.
    Task: 7-Day Workout Plan.
    Output: STRICT JSON ONLY.

    EXAMPLE JSON STRUCTURE:
    [
      {{ "day": "Mon", "focus": "Cardio", "exercises": ["Run"], "benefit": "Heart" }},
      {{ "day": "Tue", "focus": "Strength", "exercises": ["Squats"], "benefit": "Legs" }}
    ]

    GENERATE 7 DAYS NOW:
    """

    # CHANGED: temperature from 0.4 to 0.1
    plan = query_ollama(prompt, system_instruction="Return JSON Array only.", temperature=0.1)

    if not plan or not isinstance(plan, list) or len(plan) == 0:
        logger.warning("❌ AI WORKOUT FAILED. Using Fallback.")
        plan = FALLBACK_WORKOUT_PLAN

    return jsonify(plan)


@main_bp.route('/get_recipe', methods=['POST'])
def get_recipe():
    data = request.json
    title = data.get('meal_title')

    prompt = f"Create recipe for {title}. JSON: {{ 'steps': ['1...', '2...'], 'macros': {{ 'protein': '30g', 'carbs': '20g', 'fats': '10g' }} }}"

    recipe = query_ollama(prompt, system_instruction="Chef. JSON Only.", temperature=0.3)
    return jsonify(recipe or {"steps": ["Cook ingredients.", "Serve hot."],
                              "macros": {"protein": "20g", "carbs": "20g", "fats": "10g"}})


@main_bp.route('/generate_shopping_list', methods=['POST'])
def generate_shopping_list():
    prompt = "Healthy shopping list. JSON: {{ 'Produce': ['Apple'], 'Protein': ['Egg'], 'Pantry': ['Oil'] }}"
    shopping = query_ollama(prompt, system_instruction="Helper. JSON Only.", temperature=0.2)
    return jsonify(shopping or {"Produce": ["Spinach", "Apples"], "Protein": ["Chicken"], "Pantry": ["Rice"]})


@main_bp.route('/chat_agent', methods=['POST'])
def chat_agent():
    data = request.json
    session = get_session(data.get('token'))
    user_msg = data.get('message')

    rag_context = retrieve_relevant_context(session, user_msg)
    summary = session.get('blood_context', {}).get('summary', 'No data.')

    system_prompt = f"""
    Medical Assistant.
    CONTEXT: {summary}
    EVIDENCE: {rag_context}
    If user asks for BMI/Calories calculation, output JSON: {{ "tool": "calculate_bmi", ... }}
    Otherwise output JSON: {{ "response": "Your answer..." }}
    """

    resp = query_ollama(user_msg, system_instruction=system_prompt, tools_enabled=True)

    history = session.get('chat_history', [])
    history.append({"role": "user", "text": user_msg})
    if resp and 'response' in resp:
        history.append({"role": "ai", "text": resp['response']})

    return jsonify(resp or {"response": "I'm having trouble analyzing that."})