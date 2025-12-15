import os
import json
import logging
import pdfplumber
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER
from utils import get_session, query_ollama

logger = logging.getLogger(__name__)
main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/init_context', methods=['POST'])
def init_context():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    token = request.form.get('token')

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # 1. Extract Text
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages: text += (page.extract_text() or "") + "\n"
    except Exception as e:
        logger.error(f"Failed to parse PDF: {e}")
        return jsonify({"error": "PDF Parsing Error"}), 500

    # 2. Advanced Analysis Prompt
    logger.info(f"📄 ANALYZING PDF: {len(text)} chars.")

    system_prompt = """
    You are a Functional Medicine AI. 
    Analyze the bloodwork data provided. 
    Identify markers that are out of optimal range.
    Return STRICT JSON.
    """

    user_prompt = f"""
    DATA: {text[:6000]}

    TASK: Create a health summary and strategy list.
    FORMAT:
    {{
        "patient_summary": "2-3 sentences summarizing overall health.",
        "flagged_biomarkers": [
            {{ "name": "Vitamin D", "status": "Low", "implication": "Immune & Mood issues" }}
        ],
        "strategies": [
            {{ "name": "Metabolic Reset", "desc": "Focus on insulin sensitivity via low-GI foods." }},
            {{ "name": "Anti-Inflammatory", "desc": "Reduce CRP levels with Omega-3s." }}
        ]
    }}
    """

    data = query_ollama(user_prompt, system_instruction=system_prompt)

    if not data:
        data = {"patient_summary": "Analysis failed.", "strategies": []}

    # Save to session
    session = get_session(token)
    session["blood_context"] = data
    return jsonify(data)


@main_bp.route('/generate_week', methods=['POST'])
def generate_week():
    data = request.json
    session = get_session(data.get('token'))
    strategy = data.get('strategy_name')
    context = session.get('blood_context', {})

    system_prompt = f"""
    You are a Nutritionist. 
    Patient Context: {context.get('patient_summary', 'None')}
    Selected Strategy: {strategy}
    """

    user_prompt = """
    Create a 7-Day Dinner Plan formatted as JSON.
    FORMAT:
    [
        { "day": "Mon", "title": "Meal Name", "ingredients": ["A", "B"], "benefit": "Why this matches the strategy" }
    ]
    """

    plan = query_ollama(user_prompt, system_instruction=system_prompt)

    # Fallback if AI fails completely
    if not plan:
        plan = [{"day": "Error", "title": "Could not generate", "ingredients": [], "benefit": "Try again"}]

    session["weekly_plan"] = plan
    return jsonify(plan)


@main_bp.route('/chat_agent', methods=['POST'])
def chat_agent():
    data = request.json
    session = get_session(data.get('token'))
    user_msg = data.get('message')

    # RAG-Lite: Inject Summary into System Prompt
    blood_data = session.get('blood_context', {})
    summary = blood_data.get('patient_summary', "No medical data.")

    system_prompt = f"""
    You are a Health Assistant.
    USER MEDICAL DATA: {summary}
    Keep answers short, encouraging, and based on the data.
    Return JSON: {{ "response": "Your answer here" }}
    """

    # Add History Context
    history = session.get('chat_history', [])[-5:]  # Last 5 messages
    chat_context = "\n".join([f"{h['role']}: {h['text']}" for h in history])

    user_prompt = f"""
    HISTORY:
    {chat_context}

    USER: "{user_msg}"
    """

    resp = query_ollama(user_prompt, system_instruction=system_prompt)

    if resp and 'response' in resp:
        # Update Session History
        history = session.get('chat_history', [])
        history.append({"role": "user", "text": user_msg})
        history.append({"role": "ai", "text": resp['response']})
        session['chat_history'] = history
        return jsonify(resp)

    return jsonify({"response": "I'm having trouble connecting. Please try again."})