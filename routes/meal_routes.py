import logging
from flask import Blueprint, request, jsonify
from utils import get_session, query_ollama
from data.fallbacks import FALLBACK_MEAL_PLAN

logger = logging.getLogger(__name__)
meal_bp = Blueprint('meal_bp', __name__)

@meal_bp.route('/generate_week', methods=['POST'])
def generate_week():
    data = request.json
    session = get_session(data.get('token'))

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
        # FIXED: Use the global variable directly, do NOT import it
        plan = FALLBACK_MEAL_PLAN

    session['weekly_plan'] = plan
    return jsonify(plan)


@meal_bp.route('/get_recipe', methods=['POST'])
def get_recipe():
    data = request.json
    title = data.get('meal_title')
    prompt = f"Create recipe for {title}. JSON: {{ 'steps': ['1...', '2...'], 'macros': {{ 'protein': '30g', 'carbs': '20g', 'fats': '10g' }} }}"
    recipe = query_ollama(prompt, system_instruction="Chef. JSON Only.", temperature=0.3)
    return jsonify(recipe or {"steps": ["Cook ingredients.", "Serve hot."],
                              "macros": {"protein": "20g", "carbs": "20g", "fats": "10g"}})


@meal_bp.route('/generate_shopping_list', methods=['POST'])
def generate_shopping_list():
    data = request.json
    session = get_session(data.get('token'))
    weekly_plan = session.get('weekly_plan', [])

    if not weekly_plan:
        prompt = "Healthy shopping list. JSON: {{ 'Produce': ['Apple'], 'Protein': ['Egg'], 'Pantry': ['Oil'] }}"
    else:
        # Extract meal titles to keep prompt short
        meal_titles = []
        for day in weekly_plan:
            if 'meals' in day:
                meal_titles.extend([m.get('title', 'Meal') for m in day['meals']])

        prompt = f"""
        Generate a consolidated shopping list for these meals: {", ".join(meal_titles[:25])}
        Group by category (Produce, Meat/Protein, Pantry, Dairy, Frozen).
        OUTPUT JSON ONLY: {{ 'Produce': ['Apple', ...], ... }}
        """

    shopping = query_ollama(prompt, system_instruction="Helper. JSON Only.", temperature=0.2)
    return jsonify(shopping or {"Produce": ["Spinach", "Apples"], "Protein": ["Chicken"], "Pantry": ["Rice"]})


@meal_bp.route('/propose_meal_strategies', methods=['POST'])
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
