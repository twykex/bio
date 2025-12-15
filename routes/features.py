import logging
from flask import Blueprint, request, jsonify
from ollama_client import query_ollama

features_bp = Blueprint('features', __name__)
logger = logging.getLogger(__name__)

@features_bp.route('/suggest_supplement', methods=['POST'])
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

@features_bp.route('/check_food_interaction', methods=['POST'])
def check_food_interaction():
    data = request.json
    item1 = data.get('item1', '')
    item2 = data.get('item2', '')
    prompt = f"Check interaction between {item1} and {item2}. Output JSON: {{ 'interaction': 'Safe/Caution/Danger', 'details': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "interaction": "Caution (Fallback)",
        "details": "Could not verify interaction safely. Please consult a medical professional before combining."
    })

@features_bp.route('/recipe_variation', methods=['POST'])
def recipe_variation():
    data = request.json
    recipe = data.get('recipe', 'the dish')
    variation_type = data.get('type', 'healthy')
    prompt = f"Create a {variation_type} variation of {recipe}. Output JSON: {{ 'recipe': '...', 'changes': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "recipe": f"{variation_type} {recipe}",
        "changes": "Substituted heavy ingredients for lighter alternatives. Adjusted cooking method to retain nutrients."
    })

@features_bp.route('/flavor_pairing', methods=['POST'])
def flavor_pairing():
    data = request.json
    ingredient = data.get('ingredient', '')
    prompt = f"Suggest 3 spices or flavors that pair well with {ingredient}. Output JSON: {{ 'pairings': ['...', '...', '...'] }}"
    return jsonify(query_ollama(prompt) or {
        "pairings": ["Garlic", "Lemon Zest", "Thyme"]
    })

@features_bp.route('/quick_snack', methods=['POST'])
def quick_snack():
    data = request.json
    preference = data.get('preference', 'healthy')
    prompt = f"Suggest a quick snack involving {preference}. Output JSON: {{ 'snack': '...', 'calories': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "snack": "Apple slices with Almond Butter",
        "calories": "~200 kcal"
    })

@features_bp.route('/hydration_tip', methods=['POST'])
def hydration_tip():
    data = request.json
    activity = data.get('activity', 'sedentary')
    prompt = f"Give a hydration tip for someone who is {activity}. Output JSON: {{ 'tip': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "tip": "Aim to drink at least 8 glasses (2 liters) of water daily. Increase intake if active or in hot weather."
    })

@features_bp.route('/mood_food', methods=['POST'])
def mood_food():
    data = request.json
    mood = data.get('mood', 'neutral')
    prompt = f"Suggest a food that helps with {mood} mood. Output JSON: {{ 'food': '...', 'why': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "food": "Dark Chocolate (>70%)",
        "why": "Contains compounds that may improve mood and reduce stress hormones."
    })

@features_bp.route('/energy_booster', methods=['POST'])
def energy_booster():
    data = request.json
    context = data.get('context', 'general')
    prompt = f"Suggest a natural energy boosting food for {context}. Output JSON: {{ 'food': '...', 'benefit': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "food": "Banana",
        "benefit": "Rich in potassium and natural sugars for a quick, sustained energy boost."
    })

@features_bp.route('/recovery_meal', methods=['POST'])
def recovery_meal():
    data = request.json
    workout = data.get('workout', 'general')
    prompt = f"Suggest a post-workout recovery meal for {workout}. Output JSON: {{ 'meal': '...', 'nutrients': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "meal": "Grilled Chicken with Quinoa and Avocado",
        "nutrients": "High protein for muscle repair, complex carbs for glycogen replenishment, and healthy fats."
    })

@features_bp.route('/sleep_aid', methods=['POST'])
def sleep_aid():
    data = request.json
    issue = data.get('issue', 'general')
    prompt = f"Suggest a food or drink to help sleep for {issue}. Output JSON: {{ 'recommendation': '...', 'mechanism': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "recommendation": "Chamomile Tea or Warm Milk",
        "mechanism": "Contains compounds like apigenin or tryptophan that promote relaxation and better sleep."
    })

@features_bp.route('/digestive_aid', methods=['POST'])
def digestive_aid():
    data = request.json
    symptom = data.get('symptom', 'general')
    prompt = f"Suggest a food to help with {symptom} digestion. Output JSON: {{ 'food': '...', 'benefit': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "food": "Ginger Tea",
        "benefit": "Known to alleviate nausea and settle the stomach."
    })

@features_bp.route('/immunity_booster', methods=['POST'])
def immunity_booster():
    data = request.json
    season = data.get('season', 'general')
    prompt = f"Suggest immunity-boosting foods for {season}. Output JSON: {{ 'foods': ['...', '...'] }}"
    return jsonify(query_ollama(prompt) or {
        "foods": ["Citrus Fruits (Vitamin C)", "Garlic", "Ginger", "Spinach"]
    })

@features_bp.route('/anti_inflammatory', methods=['POST'])
def anti_inflammatory():
    data = request.json
    condition = data.get('condition', 'general')
    prompt = f"Suggest anti-inflammatory foods for {condition}. Output JSON: {{ 'foods': ['...', '...'] }}"
    return jsonify(query_ollama(prompt) or {
        "foods": ["Fatty Fish (Salmon)", "Berries", "Turmeric", "Green Tea"]
    })

@features_bp.route('/antioxidant_rich', methods=['POST'])
def antioxidant_rich():
    data = request.json
    preference = data.get('preference', 'any')
    prompt = f"Suggest antioxidant-rich foods, preference: {preference}. Output JSON: {{ 'foods': ['...', '...'] }}"
    return jsonify(query_ollama(prompt) or {
        "foods": ["Blueberries", "Dark Chocolate", "Pecans", "Artichokes"]
    })

@features_bp.route('/low_gi_option', methods=['POST'])
def low_gi_option():
    data = request.json
    food = data.get('food', 'high GI food')
    prompt = f"Suggest a low GI alternative to {food}. Output JSON: {{ 'alternative': '...', 'gi_diff': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "alternative": "Quinoa or Brown Rice",
        "gi_diff": "Significantly lower Glycemic Index, providing more stable blood sugar levels."
    })

@features_bp.route('/high_protein_option', methods=['POST'])
def high_protein_option():
    data = request.json
    food = data.get('food', 'food')
    prompt = f"Suggest a high protein alternative to {food}. Output JSON: {{ 'alternative': '...', 'protein_content': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "alternative": "Greek Yogurt or Chicken Breast",
        "protein_content": "Contains significantly more protein per serving."
    })

@features_bp.route('/fiber_rich_option', methods=['POST'])
def fiber_rich_option():
    data = request.json
    food = data.get('food', 'food')
    prompt = f"Suggest a fiber rich alternative to {food}. Output JSON: {{ 'alternative': '...', 'fiber_content': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "alternative": "Lentils or Chia Seeds",
        "fiber_content": "High fiber content promotes digestive health."
    })

@features_bp.route('/seasonal_swap', methods=['POST'])
def seasonal_swap():
    data = request.json
    ingredient = data.get('ingredient', 'ingredient')
    season = data.get('season', 'current')
    prompt = f"Suggest a seasonal alternative to {ingredient} for {season}. Output JSON: {{ 'swap': '...', 'reason': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "swap": "Frozen or Canned Alternative",
        "reason": "When out of season, frozen options often retain more nutrients than imported fresh produce."
    })

@features_bp.route('/budget_swap', methods=['POST'])
def budget_swap():
    data = request.json
    ingredient = data.get('ingredient', 'expensive ingredient')
    prompt = f"Suggest a cheaper alternative to {ingredient}. Output JSON: {{ 'swap': '...', 'savings': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "swap": "Beans, Lentils, or Seasonal Produce",
        "savings": "Cost-effective staples that provide similar nutritional value."
    })

@features_bp.route('/leftover_idea', methods=['POST'])
def leftover_idea():
    data = request.json
    food = data.get('food', 'leftovers')
    prompt = f"Suggest a creative way to use leftover {food}. Output JSON: {{ 'idea': '...', 'recipe_hint': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "idea": "Hearty Stir-Fry or Salad",
        "recipe_hint": "Toss with fresh vegetables and a light dressing or soy sauce."
    })


@features_bp.route('/stress_relief', methods=['POST'])
def stress_relief():
    data = request.json
    context = data.get('context', 'general')
    prompt = f"Suggest a stress relief technique for {context}. Output JSON: {{ 'technique': '...', 'steps': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "technique": "Box Breathing",
        "steps": "Inhale for 4s, hold for 4s, exhale for 4s, hold for 4s. Repeat 4 times."
    })


@features_bp.route('/focus_technique', methods=['POST'])
def focus_technique():
    data = request.json
    task = data.get('task', 'general work')
    prompt = f"Suggest a focus technique for {task}. Output JSON: {{ 'technique': '...', 'description': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "technique": "Pomodoro Technique",
        "description": "Work for 25 minutes, then take a 5-minute break. Repeat."
    })


@features_bp.route('/exercise_alternative', methods=['POST'])
def exercise_alternative():
    data = request.json
    exercise = data.get('exercise', 'running')
    reason = data.get('reason', 'injury')
    prompt = f"Suggest an alternative to {exercise} due to {reason}. Output JSON: {{ 'alternative': '...', 'benefit': '...' }}"
    return jsonify(query_ollama(prompt) or {
        "alternative": "Swimming",
        "benefit": "Low impact cardio that protects joints while building endurance."
    })
