from flask import Blueprint, request, jsonify
from utils import query_ollama

mini_apps_bp = Blueprint('mini_apps_bp', __name__)

# Advanced Configuration: Define Personality and Strictness (Temperature)
APP_CONFIGS = {
    "suggest_supplement": {
        "system": "You are a Functional Medicine Expert. Prioritize safety and evidence.",
        "prompt": "Suggest 3 supplements for focus area: '{focus}'. Output format: {{ 'supplements': [{{ 'name': '...', 'reason': '...' }}] }}",
        "temp": 0.2  # Strict
    },
    "check_food_interaction": {
        "system": "You are a Clinical Toxicologist. Be precise.",
        "prompt": "Analyze interaction between '{item1}' and '{item2}'. Output format: {{ 'status': 'Safe/Caution/Danger', 'details': '...' }}",
        "temp": 0.0  # Deterministic (Facts only)
    },
    "recipe_variation": {
        "system": "You are an Avant-Garde Chef. Be creative and flavorful.",
        "prompt": "Reinvent the recipe '{recipe}' to be '{type}'. Output format: {{ 'new_title': '...', 'changes': ['...'], 'instructions': '...' }}",
        "temp": 0.7  # High creativity
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
    }
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
    try:
        user_prompt = config["prompt"].format(**data)
    except KeyError:
        user_prompt = f"Context: {data}. Task: {config['prompt']}"

    # 2. Execute with Specific Temperature
    result = query_ollama(
        prompt=user_prompt,
        system_instruction=config["system"],
        temperature=config["temp"]
    )

    if not result:
        return jsonify({"error": "AI could not process request"}), 500

    return jsonify(result)