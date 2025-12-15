# FILENAME: mini_apps.py
from flask import Blueprint, request, jsonify
from utils import query_ollama
from routes.mini_apps_config import APP_CONFIGS, FALLBACKS

mini_apps_bp = Blueprint('mini_apps_bp', __name__)

@mini_apps_bp.route('/<action>', methods=['POST'])
def handle_mini_app(action):
    """
    Universal Intelligent Handler.
    Routes requests to the correct configuration based on action name.
    """
    if action not in APP_CONFIGS:
        return jsonify({"error": "Unknown mini-app action"}), 404

    data = request.json or {}
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
