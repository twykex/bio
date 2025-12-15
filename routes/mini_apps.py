from flask import Blueprint, request, jsonify
from utils import query_ollama

mini_apps_bp = Blueprint('mini_apps_bp', __name__)

# --- CONFIGURATION ENGINE ---
# This dictionary defines the behavior of every mini-app.
# To add a new feature, just add 4 lines here. No new routes needed.
APP_CONFIGS = {
    "suggest_supplement": {
        "system": "You are a Functional Medicine expert. Output JSON only.",
        "prompt": "Focus: {focus}. Suggest 3 supplements. Format: {{ 'supplements': [{{ 'name': '...', 'reason': '...' }}] }}"
    },
    "check_food_interaction": {
        "system": "You are a toxicology expert. Check for dangerous interactions.",
        "prompt": "Check interaction between {item1} and {item2}. Format: {{ 'status': 'Safe/Caution/Danger', 'details': '...' }}"
    },
    "recipe_variation": {
        "system": "You are a professional chef skilled in dietary restrictions.",
        "prompt": "Modify recipe '{recipe}' to be '{type}'. Format: {{ 'new_title': '...', 'changes': ['...'] }}"
    },
    "stress_relief": {
        "system": "You are a psychologist specializing in CBT.",
        "prompt": "Suggest a technique for '{context}'. Format: {{ 'technique': '...', 'steps': ['Step 1...', 'Step 2...'] }}"
    },
    "flavor_pairing": {
        "system": "You are a molecular gastronomer.",
        "prompt": "Suggest 3 pairings for {ingredient}. Format: {{ 'pairings': ['...', '...', '...'] }}"
    },
    "recovery_meal": {
        "system": "You are a sports nutritionist.",
        "prompt": "Suggest a post-workout meal for {workout}. Format: {{ 'meal': '...', 'nutrients': '...' }}"
    }
}


@mini_apps_bp.route('/<action>', methods=['POST'])
def handle_mini_app(action):
    """
    Universal Intelligent Handler.
    """
    if action not in APP_CONFIGS:
        return jsonify({"error": "Unknown tool"}), 404

    data = request.json
    config = APP_CONFIGS[action]

    # Dynamic Prompt Injection
    # e.g. Replaces {focus} in the prompt with data['focus']
    try:
        user_prompt = config["prompt"].format(**data)
    except KeyError as e:
        # Fallback if frontend sends wrong keys
        user_prompt = f"Context: {str(data)}. Task: {config['prompt']}"

    result = query_ollama(
        prompt=user_prompt,
        system_instruction=config["system"],
        temperature=0.3  # Low temperature for factual/tool responses
    )

    if not result:
        return jsonify({"error": "AI could not process request"}), 500

    return jsonify(result)