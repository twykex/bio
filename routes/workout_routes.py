import logging
from flask import Blueprint, request, jsonify
from utils import get_session, query_ollama
from data.fallbacks import FALLBACK_WORKOUT_PLAN

logger = logging.getLogger(__name__)
workout_bp = Blueprint('workout_bp', __name__)

@workout_bp.route('/generate_workout', methods=['POST'])
def generate_workout():
    data = request.json
    session = get_session(data.get('token'))
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

    return jsonify(plan)


@workout_bp.route('/propose_fitness_strategies', methods=['POST'])
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