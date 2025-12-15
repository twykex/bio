### FILENAME: main_routes.py ###
import os
import json
import logging
import pdfplumber
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER
from utils import get_session, query_ollama, get_embedding, retrieve_relevant_context, analyze_image, save_session

logger = logging.getLogger(__name__)
main_bp = Blueprint('main_bp', __name__)

# --- FALLBACK DATA ---
FALLBACK_MEAL_PLAN = [
    {
        "day": "Mon",
        "meals": [
            {"type": "Breakfast", "title": "Oatmeal & Berries", "calories": 350, "protein": "12g", "carbs": "60g", "fats": "6g", "benefit": "Sustained Energy"},
            {"type": "Lunch", "title": "Grilled Chicken Salad", "calories": 450, "protein": "40g", "carbs": "15g", "fats": "20g", "benefit": "Lean Protein"},
            {"type": "Dinner", "title": "Salmon & Quinoa", "calories": 550, "protein": "35g", "carbs": "45g", "fats": "25g", "benefit": "Omega-3s"},
            {"type": "Snack", "title": "Greek Yogurt", "calories": 150, "protein": "15g", "carbs": "8g", "fats": "0g", "benefit": "Gut Health"}
        ],
        "total_macros": {"calories": 1500, "protein": "102g", "carbs": "128g", "fats": "51g"}
    },
    {
        "day": "Tue",
        "meals": [
            {"type": "Breakfast", "title": "Scrambled Eggs & Toast", "calories": 400, "protein": "20g", "carbs": "30g", "fats": "18g", "benefit": "Muscle Repair"},
            {"type": "Lunch", "title": "Turkey Wrap", "calories": 420, "protein": "30g", "carbs": "35g", "fats": "12g", "benefit": "Light & Filling"},
            {"type": "Dinner", "title": "Beef Stir-Fry", "calories": 600, "protein": "45g", "carbs": "50g", "fats": "22g", "benefit": "Iron Boost"},
            {"type": "Snack", "title": "Almonds", "calories": 160, "protein": "6g", "carbs": "6g", "fats": "14g", "benefit": "Healthy Fats"}
        ],
        "total_macros": {"calories": 1580, "protein": "101g", "carbs": "121g", "fats": "66g"}
    },
    {
        "day": "Wed",
        "meals": [
            {"type": "Breakfast", "title": "Smoothie Bowl", "calories": 350, "protein": "10g", "carbs": "55g", "fats": "8g", "benefit": "Antioxidants"},
            {"type": "Lunch", "title": "Lentil Soup", "calories": 380, "protein": "18g", "carbs": "60g", "fats": "5g", "benefit": "Fiber Rich"},
            {"type": "Dinner", "title": "Roast Chicken", "calories": 550, "protein": "40g", "carbs": "30g", "fats": "25g", "benefit": "Comfort Food"},
            {"type": "Snack", "title": "Apple & Peanut Butter", "calories": 200, "protein": "4g", "carbs": "25g", "fats": "10g", "benefit": "Quick Energy"}
        ],
        "total_macros": {"calories": 1480, "protein": "72g", "carbs": "170g", "fats": "48g"}
    },
    {
        "day": "Thu",
        "meals": [
            {"type": "Breakfast", "title": "Avocado Toast", "calories": 380, "protein": "10g", "carbs": "40g", "fats": "20g", "benefit": "Healthy Fats"},
            {"type": "Lunch", "title": "Quinoa Bowl", "calories": 450, "protein": "15g", "carbs": "65g", "fats": "12g", "benefit": "Complete Protein"},
            {"type": "Dinner", "title": "Baked Cod", "calories": 500, "protein": "35g", "carbs": "20g", "fats": "15g", "benefit": "Lean & Light"},
            {"type": "Snack", "title": "Hummus & Carrots", "calories": 150, "protein": "5g", "carbs": "15g", "fats": "8g", "benefit": "Crunchy Veg"}
        ],
        "total_macros": {"calories": 1480, "protein": "65g", "carbs": "140g", "fats": "55g"}
    },
    {
        "day": "Fri",
        "meals": [
            {"type": "Breakfast", "title": "Yogurt Parfait", "calories": 300, "protein": "15g", "carbs": "40g", "fats": "5g", "benefit": "Probiotics"},
            {"type": "Lunch", "title": "Tuna Salad", "calories": 400, "protein": "35g", "carbs": "10g", "fats": "20g", "benefit": "Low Carb"},
            {"type": "Dinner", "title": "Shrimp Pasta", "calories": 600, "protein": "30g", "carbs": "70g", "fats": "15g", "benefit": "Carb Load"},
            {"type": "Snack", "title": "Protein Bar", "calories": 200, "protein": "20g", "carbs": "20g", "fats": "5g", "benefit": "Recovery"}
        ],
        "total_macros": {"calories": 1500, "protein": "100g", "carbs": "140g", "fats": "45g"}
    },
    {
        "day": "Sat",
        "meals": [
            {"type": "Breakfast", "title": "Pancakes", "calories": 500, "protein": "10g", "carbs": "80g", "fats": "15g", "benefit": "Weekend Treat"},
            {"type": "Lunch", "title": "Club Sandwich", "calories": 550, "protein": "25g", "carbs": "50g", "fats": "25g", "benefit": "Classic"},
            {"type": "Dinner", "title": "Steak & Potatoes", "calories": 700, "protein": "50g", "carbs": "45g", "fats": "30g", "benefit": "High Protein"},
            {"type": "Snack", "title": "Dark Chocolate", "calories": 150, "protein": "2g", "carbs": "15g", "fats": "10g", "benefit": "Antioxidants"}
        ],
        "total_macros": {"calories": 1900, "protein": "87g", "carbs": "190g", "fats": "80g"}
    },
    {
        "day": "Sun",
        "meals": [
            {"type": "Breakfast", "title": "Omelette", "calories": 450, "protein": "25g", "carbs": "5g", "fats": "35g", "benefit": "Keto Start"},
            {"type": "Lunch", "title": "Cobb Salad", "calories": 500, "protein": "30g", "carbs": "10g", "fats": "35g", "benefit": "Greens"},
            {"type": "Dinner", "title": "Vegetable Curry", "calories": 450, "protein": "15g", "carbs": "60g", "fats": "15g", "benefit": "Spices"},
            {"type": "Snack", "title": "Mixed Nuts", "calories": 200, "protein": "6g", "carbs": "8g", "fats": "18g", "benefit": "Satiety"}
        ],
        "total_macros": {"calories": 1600, "protein": "76g", "carbs": "83g", "fats": "103g"}
    }
]

FALLBACK_WORKOUT_PLAN = [
    {
        "day": "Mon",
        "focus": "Full Body Strength",
        "warmup": ["5 min Jog", "Shoulder Circles", "Bodyweight Squats"],
        "exercises": [
            {"name": "Squats", "sets": "3", "reps": "12", "rpe": "8", "rest": "60s", "tip": "Keep weight in heels"},
            {"name": "Pushups", "sets": "3", "reps": "15", "rpe": "8", "rest": "45s", "tip": "Core tight"},
            {"name": "Dumbbell Rows", "sets": "3", "reps": "12", "rpe": "8", "rest": "60s", "tip": "Squeeze back"}
        ],
        "cooldown": ["Static Stretching", "Foam Roll"],
        "benefit": "Metabolic Boost"
    },
    {
        "day": "Tue",
        "focus": "Active Recovery",
        "warmup": ["5 min Walk"],
        "exercises": [
            {"name": "Light Jog", "sets": "1", "reps": "30m", "rpe": "4", "rest": "-", "tip": "Zone 2 Heart Rate"},
            {"name": "Stretching", "sets": "1", "reps": "15m", "rpe": "2", "rest": "-", "tip": "Focus on hips"}
        ],
        "cooldown": ["Deep Breathing"],
        "benefit": "Blood Flow"
    },
    {
        "day": "Wed",
        "focus": "Lower Body Power",
        "warmup": ["High Knees", "Glute Bridges"],
        "exercises": [
            {"name": "Lunges", "sets": "3", "reps": "12/leg", "rpe": "8", "rest": "60s", "tip": "Knee tracking over toe"},
            {"name": "Glute Bridge", "sets": "3", "reps": "15", "rpe": "9", "rest": "45s", "tip": "Squeeze at top"},
            {"name": "Calf Raises", "sets": "3", "reps": "20", "rpe": "9", "rest": "30s", "tip": "Full range"}
        ],
        "cooldown": ["Hamstring Stretch", "Quad Stretch"],
        "benefit": "Leg Strength"
    },
    {
        "day": "Thu",
        "focus": "Core & Stability",
        "warmup": ["Cat-Cow", "Bird-Dog"],
        "exercises": [
            {"name": "Plank", "sets": "3", "reps": "45s", "rpe": "9", "rest": "30s", "tip": "Don't sag hips"},
            {"name": "Dead Bug", "sets": "3", "reps": "12/side", "rpe": "7", "rest": "30s", "tip": "Keep lower back flat"},
            {"name": "Side Plank", "sets": "2", "reps": "30s/side", "rpe": "8", "rest": "30s", "tip": "Lift hips high"}
        ],
        "cooldown": ["Child's Pose"],
        "benefit": "Core Stability"
    },
    {
        "day": "Fri",
        "focus": "HIIT",
        "warmup": ["Jumping Jacks", "Arm Swings"],
        "exercises": [
            {"name": "Burpees", "sets": "4", "reps": "30s", "rpe": "10", "rest": "30s", "tip": "Explosive movement"},
            {"name": "Mountain Climbers", "sets": "4", "reps": "30s", "rpe": "9", "rest": "30s", "tip": "Fast pace"},
            {"name": "Jump Squats", "sets": "4", "reps": "30s", "rpe": "10", "rest": "30s", "tip": "Soft landing"}
        ],
        "cooldown": ["Slow Walk", "Full Body Stretch"],
        "benefit": "Fat Burning"
    },
    {
        "day": "Sat",
        "focus": "Outdoor Activity",
        "warmup": ["Dynamic Warmup"],
        "exercises": [
            {"name": "Hiking / Cycling", "sets": "1", "reps": "60m", "rpe": "6", "rest": "-", "tip": "Enjoy nature"}
        ],
        "cooldown": ["Hydrate"],
        "benefit": "Mental Health"
    },
    {
        "day": "Sun",
        "focus": "Rest & Restore",
        "warmup": ["None"],
        "exercises": [
            {"name": "Meditation", "sets": "1", "reps": "10m", "rpe": "1", "rest": "-", "tip": "Focus on breath"},
            {"name": "Foam Rolling", "sets": "1", "reps": "15m", "rpe": "3", "rest": "-", "tip": "Target sore spots"}
        ],
        "cooldown": ["Nap"],
        "benefit": "Recovery"
    }
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
    safe_chunks = chunks[:60]
    embeddings = [get_embedding(chunk) for chunk in safe_chunks]

    session = get_session(token)
    session['raw_text_chunks'] = safe_chunks
    session['embeddings'] = embeddings

    system_prompt = "You are a Functional Doctor. Diagnose the user. Return strict JSON."
    user_prompt = f"""
    DATA: {text[:8000]}

    TASK: Identify the top 3 health issues from this bloodwork.
    For each issue, provide 2 distinct ways to fix it (e.g., Diet vs. Lifestyle).

    OUTPUT JSON FORMAT:
    {{
        "patient_name": "User",
        "health_score": 78,
        "summary": "Short overall health summary.",
        "biomarkers": [
            {{ "name": "Vitamin D", "value": "18", "unit": "ng/mL", "status": "Low" }},
            {{ "name": "Hemoglobin", "value": "14.5", "unit": "g/dL", "status": "Normal" }}
        ],
        "issues": [
            {{
                "title": "Low Vitamin D",
                "severity": "High",
                "value": "18 ng/mL",
                "explanation": "This explains your low energy and weak immunity.",
                "options": [
                    {{ "type": "Dietary", "text": "Eat fatty fish & fortified foods." }},
                    {{ "type": "Lifestyle", "text": "20 mins morning sun exposure." }}
                ]
            }}
        ]
    }}
    """

    data = query_ollama(user_prompt, system_instruction=system_prompt, temperature=0.1)

    if not data or 'issues' not in data:
        data = {
            "patient_name": "Guest",
            "health_score": 75,
            "summary": "We detected some potential optimizations for your metabolism.",
            "biomarkers": [
                {"name": "Glucose", "value": "95", "unit": "mg/dL", "status": "Normal"},
                {"name": "HbA1c", "value": "5.7", "unit": "%", "status": "Borderline"},
                {"name": "Cholesterol", "value": "190", "unit": "mg/dL", "status": "Normal"},
                {"name": "Vitamin D", "value": "30", "unit": "ng/mL", "status": "Normal"}
            ],
            "strategies": [
                {"name": "Metabolic Reset", "desc": "Focus on insulin sensitivity and inflammation reduction."},
                {"name": "Energy Optimization", "desc": "Targeting mitochondrial health and fatigue."},
                {"name": "Balanced Approach", "desc": "Sustainable lifestyle changes for long term health."}
            ],
            "issues": [
                {
                    "title": "Metabolic Efficiency",
                    "severity": "Medium",
                    "value": "Sub-optimal",
                    "explanation": "Your markers suggest insulin resistance risk.",
                    "options": [{"type": "Diet", "text": "Low Carb Protocol"},
                                {"type": "Activity", "text": "Zone 2 Cardio"}]
                },
                {
                    "title": "Inflammation Levels",
                    "severity": "Low",
                    "value": "Elevated",
                    "explanation": "Slightly high CRP indicates stress on the body.",
                    "options": [{"type": "Diet", "text": "Anti-Inflammatory Foods"},
                                {"type": "Supplement", "text": "Omega-3 Protocol"}]
                }
            ]
        }

    session["blood_context"] = data
    save_session(token)
    return jsonify(data)


@main_bp.route('/generate_week', methods=['POST'])
def generate_week():
    data = request.json
    token = data.get('token')
    session = get_session(token)

    summary = session.get('blood_context', {}).get('summary', 'General Health')
    blood_strategies = data.get('blood_strategies', [])
    lifestyle = data.get('lifestyle', {})

    logger.info(f"🍳 ARCHITECTING PLAN: {lifestyle.get('cuisine')} | {lifestyle.get('time')} | {summary}")

    prompt = f"""
    ROLE: Elite Nutritionist.

    PATIENT PROFILE:
    - BIOLOGY: {summary}
    - PRIORITY FIXES: {", ".join(blood_strategies)}
    - GENDER: {lifestyle.get('gender', 'Not Specified')}
    - AGE: {lifestyle.get('age', 'Not Specified')}
    - ACTIVITY: {lifestyle.get('activity', 'Not Specified')}
    - GOAL: {lifestyle.get('goal', 'General Health')}
    - MOTIVATION: {lifestyle.get('motivation', 'General Wellness')}
    - SLEEP: {lifestyle.get('sleep', 'Normal')}
    - STRESS: {lifestyle.get('stress', 'Moderate')}

    LIFESTYLE CONSTRAINTS:
    - CUISINE STYLE: {lifestyle.get('cuisine', 'Varied')}
    - COOKING TIME: {lifestyle.get('time', '30 mins')}
    - COOKING SKILL: {lifestyle.get('cooking_skill', 'Intermediate')}
    - BUDGET: {lifestyle.get('budget', 'Moderate')}
    - DIET TYPE: {lifestyle.get('diet', 'Balanced')}
    - MEAL FREQUENCY: {lifestyle.get('meals', '3 Meals')}
    - HYDRATION HABIT: {lifestyle.get('hydration', 'Average')}
    - ALLERGIES/EXCLUSIONS: {lifestyle.get('allergies', 'None')}

    TASK: Create a 7-Day Full Day Meal Plan (Breakfast, Lunch, Dinner, Snack).
    Include estimated macros for each meal and a daily total.
    OUTPUT: STRICT JSON ARRAY ONLY.

    EXAMPLE:
    [
      {{
        "day": "Mon",
        "meals": [
          {{ "type": "Breakfast", "title": "Oatmeal", "calories": 300, "protein": "10g", "carbs": "50g", "fats": "5g", "benefit": "Fiber" }},
          {{ "type": "Lunch", "title": "Salad", "calories": 400, "protein": "30g", "carbs": "10g", "fats": "20g", "benefit": "Greens" }},
          {{ "type": "Dinner", "title": "Chicken", "calories": 500, "protein": "40g", "carbs": "20g", "fats": "15g", "benefit": "Protein" }},
          {{ "type": "Snack", "title": "Apple", "calories": 80, "protein": "0g", "carbs": "20g", "fats": "0g", "benefit": "Energy" }}
        ],
        "total_macros": {{ "calories": 1280, "protein": "80g", "carbs": "100g", "fats": "40g" }}
      }}
    ]

    GENERATE 7 DAYS NOW:
    """

    plan = query_ollama(prompt, system_instruction="Return JSON Array only.", temperature=0.3)

    if isinstance(plan, dict) and 'plan' in plan: plan = plan['plan']

    if not plan or not isinstance(plan, list) or len(plan) == 0:
        logger.warning("❌ AI PLAN FAILED. Using Fallback.")
        plan = FALLBACK_MEAL_PLAN

    session['weekly_plan'] = plan
    save_session(token)
    return jsonify(plan)


@main_bp.route('/generate_workout', methods=['POST'])
def generate_workout():
    data = request.json
    token = data.get('token')
    session = get_session(token)
    strategy = data.get('strategy_name', 'General')
    lifestyle = data.get('lifestyle', {})
    fitness_strategy = data.get('fitness_strategy', strategy) # Use specific fitness strategy if available

    logger.info(f"💪 Generating Workout for: {fitness_strategy}")

    prompt = f"""
    ROLE: Elite Personal Trainer.

    CLIENT PROFILE:
    - GOAL: {lifestyle.get('goal', 'General Fitness')}
    - MOTIVATION: {lifestyle.get('motivation', 'General Wellness')}
    - ACTIVITY LEVEL: {lifestyle.get('activity', 'Moderate')}
    - GENDER: {lifestyle.get('gender', 'Not Specified')}
    - AGE: {lifestyle.get('age', 'Not Specified')}
    - SLEEP QUALITY: {lifestyle.get('sleep', 'Normal')}
    - STRESS LEVEL: {lifestyle.get('stress', 'Moderate')}
    - LIMITATIONS: {lifestyle.get('limitations', 'None')}
    - EQUIPMENT: {lifestyle.get('equipment', 'Basic Home Gym')}

    STRATEGY FOCUS: {fitness_strategy}

    TASK: Create a 7-day workout schedule.
    Include Warmup, Main Workout, and Cooldown.

    Format: JSON Array:
    [
        {{
            "day": "Mon",
            "focus": "Upper Body",
            "warmup": ["Arm Circles", "Band Pull Aparts"],
            "exercises": [
                {{ "name": "Bench Press", "sets": "3", "reps": "8", "rpe": "8", "rest": "90s", "tip": "Retract scapula" }}
            ],
            "cooldown": ["Chest Stretch"],
            "benefit": "Strength"
        }}
    ]
    """

    plan = query_ollama(prompt, system_instruction="You are a Trainer. Return JSON Array only.", temperature=0.1)

    if not plan or not isinstance(plan, list) or len(plan) == 0:
        logger.warning("❌ AI WORKOUT FAILED. Using Fallback.")
        plan = FALLBACK_WORKOUT_PLAN

    session['workout_plan'] = plan
    save_session(token)
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
    token = data.get('token')
    session = get_session(token)
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

    save_session(token)
    return jsonify(resp or {"response": "I'm having trouble analyzing that."})


@main_bp.route('/propose_meal_strategies', methods=['POST'])
def propose_meal_strategies():
    data = request.json
    session = get_session(data.get('token'))
    summary = session.get('blood_context', {}).get('summary', 'General Health')

    # Ask AI to brainstorm 3 distinct approaches based on bloodwork
    prompt = f"""
    ROLE: Elite Medical Nutritionist.
    PATIENT CONTEXT: {summary}

    TASK: Propose 3 distinct weekly meal plan strategies to fix the patient's issues.
    1. "Aggressive Repair": Hardcore focus on biomarkers.
    2. "Balanced Lifestyle": 80/20 rule, easier to stick to.
    3. "Time Saver": Dense nutrients, fast prep.

    OUTPUT: JSON Array only.
    [
        {{ "id": "repair", "title": "Aggressive Repair", "desc": "Strict protocol to fix Vitamin D & Iron fast.", "pros": "Fastest Results" }},
        {{ "id": "balance", "title": "Balanced Flow", "desc": "Sustainable approach allowing some flexibility.", "pros": "High Adherence" }},
        {{ "id": "quick", "title": "Metabolic Quick", "desc": "15-min meals focused on insulin control.", "pros": "Best for Busy Schedule" }}
    ]
    """

    strategies = query_ollama(prompt, system_instruction="Return JSON Array only.", temperature=0.4)

    # Fallback
    if not strategies or not isinstance(strategies, list):
        strategies = [
            {"id": "repair", "title": "Biomarker Repair", "desc": "Focus strictly on optimizing your blood results.",
             "pros": "Fastest Improvement"},
            {"id": "balance", "title": "Balanced Lifestyle", "desc": "A sustainable mix of health and flavor.",
             "pros": "Easy to stick to"},
            {"id": "quick", "title": "High Performance", "desc": "Nutrient dense meals for high energy.",
             "pros": "Best for Focus"}
        ]

    return jsonify(strategies)


@main_bp.route('/analyze_food_plate', methods=['POST'])
def analyze_food_plate():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']

    prompt = """
    TASK: Analyze this food image.
    Identify the meal and estimate macros.
    OUTPUT JSON ONLY:
    {
        "meal_name": "Grilled Salmon",
        "ingredients": ["Salmon", "Asparagus", "Rice"],
        "macros": { "calories": 450, "protein": "40g", "carbs": "30g", "fats": "15g" },
        "health_score": 85
    }
    """

    result = analyze_image(file, prompt)

    if not result:
        # Fallback Mock for Demo/Dev
        result = {
            "meal_name": "Detected Meal",
            "ingredients": ["Protein Source", "Vegetables", "Carb Source"],
            "macros": { "calories": 500, "protein": "30g", "carbs": "40g", "fats": "20g" },
            "health_score": 80
        }

    return jsonify(result)


@main_bp.route('/generate_supplement_stack', methods=['POST'])
def generate_supplement_stack():
    data = request.json
    session = get_session(data.get('token'))
    current_meds = data.get('current_meds', [])
    summary = session.get('blood_context', {}).get('summary', 'General Health')

    prompt = f"""
    ROLE: Clinical Pharmacist & Functional Doctor.
    PATIENT SUMMARY: {summary}
    CURRENT MEDS/SUPPS: {", ".join(current_meds) if current_meds else "None"}

    TASK: Design a supplement stack.
    1. Address the patient's issues.
    2. CHECK FOR INTERACTIONS with current meds.

    OUTPUT JSON ONLY:
    {{
        "stack": [
            {{ "name": "Magnesium Glycinate", "dosage": "400mg", "reason": "Sleep & Anxiety", "interaction_warning": "None" }}
        ],
        "warnings": "Avoid taking Magnesium with antibiotic X."
    }}
    """

    stack = query_ollama(prompt, system_instruction="Return JSON Only.", temperature=0.2)

    if not stack:
        stack = {
            "stack": [
                { "name": "Vitamin D3 + K2", "dosage": "5000 IU", "reason": "Immune Support", "interaction_warning": "None" },
                { "name": "Omega-3", "dosage": "2g", "reason": "Inflammation", "interaction_warning": "Check blood thinners" }
            ],
            "warnings": "Always consult your doctor."
        }

    return jsonify(stack)


@main_bp.route('/propose_fitness_strategies', methods=['POST'])
def propose_fitness_strategies():
    data = request.json
    session = get_session(data.get('token'))
    summary = session.get('blood_context', {}).get('summary', 'General Health')
    lifestyle = data.get('lifestyle', {})

    prompt = f"""
    ROLE: Elite Strength & Conditioning Coach.
    CLIENT GOAL: {lifestyle.get('goal', 'General Fitness')}
    SUMMARY: {summary}

    TASK: Propose 3 distinct training strategies.
    1. "Hypertrophy": Muscle building focus.
    2. "Metabolic Conditioning": Fat loss/endurance.
    3. "Functional Strength": Mobility and real-world strength.

    OUTPUT: JSON Array only.
    [
        {{ "id": "build", "title": "Hypertrophy Focus", "desc": "High volume for max muscle growth.", "pros": "Aesthetics" }},
        {{ "id": "burn", "title": "Metabolic Burn", "desc": "High intensity intervals.", "pros": "Fat Loss" }},
        {{ "id": "move", "title": "Functional Flow", "desc": "Movement quality and joint health.", "pros": "Longevity" }}
    ]
    """

    strategies = query_ollama(prompt, system_instruction="Return JSON Array only.", temperature=0.4)

    if not strategies or not isinstance(strategies, list):
        strategies = [
            {"id": "build", "title": "Hypertrophy Protocol", "desc": "Optimized for muscle growth and definition.", "pros": "Max Strength"},
            {"id": "burn", "title": "Metabolic Burn", "desc": "High intensity circuit training for fat loss.", "pros": "Fat Loss"},
            {"id": "move", "title": "Functional Athlete", "desc": "Focus on mobility, stability, and real-world power.", "pros": "Pain Free"}
        ]

    return jsonify(strategies)

@main_bp.route('/get_state', methods=['POST'])
def get_state():
    data = request.json
    s = get_session(data.get('token'))
    # Return state to frontend.
    # Excluding 'raw_text_chunks' and 'embeddings' to reduce payload size as they are not needed on frontend.
    return jsonify({
        "blood_context": s.get('blood_context'),
        "weekly_plan": s.get('weekly_plan', []),
        "workout_plan": s.get('workout_plan', []),
        "chat_history": s.get('chat_history', [])
    })
