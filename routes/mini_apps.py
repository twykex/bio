### FILENAME: mini_apps.py ###
from flask import Blueprint, request, jsonify
from utils import query_ollama

mini_apps_bp = Blueprint('mini_apps_bp', __name__)

# --- CONFIGURATION ENGINE ---
# Defines the personality (System Prompt), strictness (Temperature),
# and task format for every mini-app.
APP_CONFIGS = {
    # --- NEW: AI Tooltip Definition ---
    "define_term": {
        "system": "You are a concise medical dictionary. Define the term in 1 short sentence. No fluff.",
        "prompt": "Define '{term}' in the context of health/nutrition.",
        "temp": 0.1  # Very strict/factual
    },

    # --- Existing Tools ---
    "suggest_supplement": {
        "system": "You are a Functional Medicine Expert. Prioritize safety and evidence.",
        "prompt": "Suggest 3 supplements for focus area: '{focus}'. Output format: {{ 'supplements': [{{ 'name': '...', 'reason': '...' }}] }}",
        "temp": 0.2
    },
    "check_food_interaction": {
        "system": "You are a Clinical Toxicologist. Be precise.",
        "prompt": "Analyze interaction between '{item1}' and '{item2}'. Output format: {{ 'status': 'Safe/Caution/Danger', 'details': '...' }}",
        "temp": 0.0
    },
    "check_drug_interaction": {
        "system": "You are a Pharmacist. Check for interactions strictly.",
        "prompt": "Check interaction between: '{drug_list}'. Output format: {{ 'interactions': [{{ 'drugs': 'A + B', 'severity': 'High', 'effect': '...' }}] }}",
        "temp": 0.0
    },
    "recipe_variation": {
        "system": "You are an Avant-Garde Chef. Be creative and flavorful.",
        "prompt": "Reinvent the recipe '{recipe}' to be '{type}'. Output format: {{ 'new_title': '...', 'changes': ['...'], 'instructions': '...' }}",
        "temp": 0.7
    },
    "stress_relief": {
        "system": "You are a CBT Psychologist.",
        "prompt": "Suggest a technique for '{context}'. Output format: {{ 'technique': '...', 'steps': ['...'] }}",
        "temp": 0.4
    },
    "flavor_pairing": {
        "system": "You are a Molecular Gastronomer.",
        "prompt": "Suggest 3 unique flavor pairings for '{ingredient}'. Output format: {{ 'pairings': ['...', '...', '...'] }}",
        "temp": 0.6
    },
    # --- Additional Utilities ---
    "quick_snack": {
        "system": "You are a Nutritionist.",
        "prompt": "Suggest a snack for preference: '{preference}'. Output format: {{ 'snack': '...', 'calories': '...' }}",
        "temp": 0.5
    },
    "hydration_tip": {
        "system": "You are a Sports Scientist.",
        "prompt": "Hydration tip for activity: '{activity}'. Output format: {{ 'tip': '...' }}",
        "temp": 0.3
    },
    "mood_food": {
        "system": "You are a Nutritional Psychiatrist.",
        "prompt": "Suggest food for mood: '{mood}'. Output format: {{ 'food': '...', 'mechanism': '...' }}",
        "temp": 0.4
    },
    "energy_booster": {
        "system": "You are a Performance Coach.",
        "prompt": "Energy booster for context: '{context}'. Output format: {{ 'food': '...', 'benefit': '...' }}",
        "temp": 0.4
    },
    "recovery_meal": {
        "system": "You are a Sports Nutritionist.",
        "prompt": "Recovery meal for workout: '{workout}'. Output format: {{ 'meal': '...', 'nutrients': '...' }}",
        "temp": 0.3
    },
    "sleep_aid": {
        "system": "You are a Sleep Specialist.",
        "prompt": "Sleep aid for issue: '{issue}'. Output format: {{ 'recommendation': '...', 'why': '...' }}",
        "temp": 0.2
    },
    "digestive_aid": {
        "system": "You are a Gastroenterologist Assistant.",
        "prompt": "Digestive aid for symptom: '{symptom}'. Output format: {{ 'food': '...', 'benefit': '...' }}",
        "temp": 0.2
    },
    "immunity_booster": {
        "system": "You are an Immunologist.",
        "prompt": "Immunity booster for season: '{season}'. Output format: {{ 'foods': ['...', '...'] }}",
        "temp": 0.2
    },
    "anti_inflammatory": {
        "system": "You are an Inflammation Specialist.",
        "prompt": "Anti-inflammatory for: '{condition}'. Output format: {{ 'foods': ['...', '...'] }}",
        "temp": 0.2
    },
    "antioxidant_rich": {
        "system": "You are a Nutritionist.",
        "prompt": "Antioxidant foods for preference: '{preference}'. Output format: {{ 'foods': ['...', '...'] }}",
        "temp": 0.3
    },
    "low_gi_option": {
        "system": "You are a Dietitian.",
        "prompt": "Low GI alternative to '{food}'. Output format: {{ 'alternative': '...', 'benefit': '...' }}",
        "temp": 0.2
    },
    "high_protein_option": {
        "system": "You are a Bodybuilding Coach.",
        "prompt": "High protein alternative to '{food}'. Output format: {{ 'alternative': '...', 'protein': '...' }}",
        "temp": 0.3
    },
    "fiber_rich_option": {
        "system": "You are a Dietitian.",
        "prompt": "High fiber alternative to '{food}'. Output format: {{ 'alternative': '...', 'fiber': '...' }}",
        "temp": 0.2
    },
    "seasonal_swap": {
        "system": "You are a Sustainable Chef.",
        "prompt": "Seasonal swap for '{ingredient}' in '{season}'. Output format: {{ 'swap': '...', 'reason': '...' }}",
        "temp": 0.4
    },
    "budget_swap": {
        "system": "You are a Frugal Chef.",
        "prompt": "Cheaper alternative to '{ingredient}'. Output format: {{ 'swap': '...', 'savings': '...' }}",
        "temp": 0.3
    },
    "leftover_idea": {
        "system": "You are a Home Cook.",
        "prompt": "Idea for leftover '{food}'. Output format: {{ 'idea': '...', 'recipe': '...' }}",
        "temp": 0.6
    },
    "focus_technique": {
        "system": "You are a Productivity Coach.",
        "prompt": "Focus technique for '{task}'. Output format: {{ 'technique': '...', 'desc': '...' }}",
        "temp": 0.3
    },
    "exercise_alternative": {
        "system": "You are a Physical Therapist.",
        "prompt": "Alternative to '{exercise}' due to '{reason}'. Output format: {{ 'alternative': '...', 'benefit': '...' }}",
        "temp": 0.2
    },
    # --- New Fitness Tools ---
    "calculate_1rm": {
        "system": "You are a Strength Coach. Use the Epley Formula: w * (1 + r/30).",
        "prompt": "Estimate 1 Rep Max for {weight}kg x {reps} reps. Output format: {{ 'estimated_1rm': '...', 'training_tip': '...' }}",
        "temp": 0.1
    },
    "heart_rate_zones": {
        "system": "You are a Cardiovascular Physiologist.",
        "prompt": "Calculate heart rate zones for Age: {age}, Resting HR: {resting_hr}. Output format: {{ 'max_hr': '...', 'zone_2': '...-...' }}",
        "temp": 0.1
    },
    "exercise_form_check": {
        "system": "You are an Elite Biomechanist.",
        "prompt": "Give 3 critical form cues for '{exercise}'. Output format: {{ 'cues': ['...', '...', '...'], 'common_mistake': '...' }}",
        "temp": 0.2
    }
}

FALLBACKS = {
    "define_term": {"definition": "Loading definition..."},
    "suggest_supplement": {"supplements": [{"name": "Multivitamin", "reason": "General Wellness"}]},
    "check_food_interaction": {"status": "Safe", "details": "No known interaction."},
    "check_drug_interaction": {"interactions": []},
    "recipe_variation": {"new_title": "Varied Recipe", "changes": ["Add spice"], "instructions": "Cook as usual."},
    "stress_relief": {"technique": "Deep Breathing", "steps": ["Inhale 4s", "Hold 4s", "Exhale 4s"]},
    "flavor_pairing": {"pairings": ["Salt & Pepper", "Lemon & Garlic"]},
    "quick_snack": {"snack": "Apple", "calories": "95"},
    "hydration_tip": {"tip": "Drink water."},
    "mood_food": {"food": "Dark Chocolate", "mechanism": "Endorphins"},
    "energy_booster": {"food": "Banana", "benefit": "Potassium"},
    "recovery_meal": {"meal": "Protein Shake", "nutrients": "Protein"},
    "sleep_aid": {"recommendation": "Chamomile Tea", "why": "Relaxation"},
    "digestive_aid": {"food": "Ginger", "benefit": "Anti-nausea"},
    "immunity_booster": {"foods": ["Citrus", "Garlic"]},
    "anti_inflammatory": {"foods": ["Turmeric", "Berries"]},
    "antioxidant_rich": {"foods": ["Blueberries", "Pecans"]},
    "low_gi_option": {"alternative": "Quinoa", "benefit": "Lower spike"},
    "high_protein_option": {"alternative": "Chicken Breast", "protein": "30g"},
    "fiber_rich_option": {"alternative": "Beans", "fiber": "10g"},
    "seasonal_swap": {"swap": "Root Vegetables", "reason": "In season"},
    "budget_swap": {"swap": "Lentils", "savings": "High"},
    "leftover_idea": {"idea": "Stir fry", "recipe": "Mix with veggies"},
    "focus_technique": {"technique": "Pomodoro", "desc": "25m work, 5m rest"},
    "exercise_alternative": {"alternative": "Swimming", "benefit": "Low impact"},
    "calculate_1rm": {"estimated_1rm": "100kg", "training_tip": "Be safe"},
    "heart_rate_zones": {"max_hr": "180", "zone_2": "110-130"},
    "exercise_form_check": {"cues": ["Keep back straight"], "common_mistake": "Rounding back"}
}


@mini_apps_bp.route('/<action>', methods=['POST'])
def handle_mini_app(action):
    """
    Universal Intelligent Handler.
    Routes requests to the correct configuration based on action name.
    """
    if action not in APP_CONFIGS:
        return jsonify({"error": "Unknown mini-app action"}), 404

    data = request.json
    config = APP_CONFIGS[action]

    # 1. Dynamic Prompt Injection
    # e.g., Replaces {term} with data['term']
    try:
        user_prompt = config["prompt"].format(**data)
    except KeyError:
        # Fallback if frontend sends slightly wrong keys
        user_prompt = f"Context: {data}. Task: {config['prompt']}"

    # 2. Execute with Specific Temperature
    # Low temp = factual (Medical), High temp = creative (Cooking)
    result = query_ollama(
        prompt=user_prompt,
        system_instruction=config["system"],
        temperature=config["temp"]
    )

    if not result:
        # Fallback
        if action in FALLBACKS:
            return jsonify(FALLBACKS[action])
        return jsonify({"error": "AI could not process request"}), 500

    return jsonify(result)