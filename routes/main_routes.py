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
                # Chunking by paragraphs (approximate)
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

    # 1. Parse & Chunk
    text, chunks = advanced_pdf_parse(filepath)

    # CRITICAL FIX: Limit chunks to prevent timeout on large PDFs
    # Only embed the first 20 chunks for the prototype
    safe_chunks = chunks[:50]

    # 2. Vector Embeddings (RAG Setup)
    embeddings = [get_embedding(chunk) for chunk in safe_chunks]

    session = get_session(token)
    session['raw_text_chunks'] = safe_chunks
    session['embeddings'] = embeddings

    # 3. FEW-SHOT PROMPTING
    few_shot = """
    EXAMPLE: "HbA1c 6.0% (4.0-5.6)" -> { "name": "HbA1c", "value": "6.0", "status": "High", "implication": "Pre-diabetes risk" }
    """

    system_prompt = f"""
    You are a Functional Medicine AI. Analyze the bloodwork.
    Refer to these extraction examples: {few_shot}
    """

    user_prompt = f"""
    DATA: {text[:8000]}
    TASK: Output JSON.
    STRUCTURE: {{ 
        "summary": "Short health summary", 
        "strategies": [ {{ "name": "Strategy Name", "desc": "Description" }} ] 
    }}
    """

    data = query_ollama(user_prompt, system_instruction=system_prompt, temperature=0.1)

    if not data:
        data = {"summary": "Analysis failed.", "strategies": []}

    session["blood_context"] = data
    return jsonify(data)


@main_bp.route('/generate_week', methods=['POST'])
def generate_week():
    data = request.json
    session = get_session(data.get('token'))
    summary = session.get('blood_context', {}).get('summary', '')
    strategy = data.get('strategy_name', 'General')
    preferences = data.get('preferences', 'None')

    prompt = f"""
    Role: Nutritionist.
    Context: {summary}. 
    Strategy: {strategy}.
    Preferences: {preferences}.
    Task: 7-Day Dinner Plan.
    Format: JSON Array of objects: {{ "day": "Mon", "title": "Meal Name", "ingredients": ["A", "B"], "benefit": "Why" }}
    """

    plan = query_ollama(prompt, system_instruction="You are a Nutritionist.", temperature=0.5)

    # Validation: Ensure it's a list
    if isinstance(plan, dict) and 'plan' in plan:
        plan = plan['plan']

    return jsonify(plan or [])


# --- ADDED MISSING ROUTE ---
@main_bp.route('/generate_workout', methods=['POST'])
def generate_workout():
    data = request.json
    session = get_session(data.get('token'))
    strategy = data.get('strategy_name', 'General')

    prompt = f"""
    Create a 7-day workout schedule for strategy: {strategy}.
    Format: JSON Array: [{{ "day": "Mon", "focus": "Cardio", "exercises": ["Run"], "benefit": "Heart" }}]
    """

    plan = query_ollama(prompt, system_instruction="You are a Trainer.", temperature=0.4)
    return jsonify(plan or [])


# --- ADDED MISSING ROUTE ---
@main_bp.route('/get_recipe', methods=['POST'])
def get_recipe():
    data = request.json
    title = data.get('meal_title')

    prompt = f"""
    Create a recipe for: {title}.
    Format: JSON {{ "steps": ["1...", "2..."], "macros": {{ "protein": "30g", "carbs": "20g", "fats": "10g" }} }}
    """

    recipe = query_ollama(prompt, system_instruction="You are a Chef.", temperature=0.3)
    return jsonify(recipe or {})


# --- ADDED MISSING ROUTE ---
@main_bp.route('/generate_shopping_list', methods=['POST'])
def generate_shopping_list():
    data = request.json
    # In a real app, we would look at the weekly plan in the session
    # For now, we generate based on general healthy staples
    prompt = """
    Generate a shopping list for a healthy week.
    Format: JSON {{ "Produce": ["Item 1"], "Proteins": ["Item 2"], "Pantry": ["Item 3"] }}
    """

    shopping = query_ollama(prompt, system_instruction="You are a Helper.", temperature=0.2)
    return jsonify(shopping or {})


@main_bp.route('/chat_agent', methods=['POST'])
def chat_agent():
    data = request.json
    session = get_session(data.get('token'))
    user_msg = data.get('message')

    # 1. RAG SEARCH
    rag_context = retrieve_relevant_context(session, user_msg)

    # 2. GLOBAL CONTEXT
    summary = session.get('blood_context', {}).get('summary', 'No data.')

    system_prompt = f"""
    You are a Medical Assistant.
    PATIENT SUMMARY: {summary}
    DOCUMENT EVIDENCE: {rag_context}

    INSTRUCTIONS:
    - Use the EVIDENCE to answer.
    - If calculating BMI/Calories, ask to use the tool.
    - Return JSON: {{ "response": "..." }} or {{ "tool": "..." }}
    """

    # 3. Call with Tools Enabled
    resp = query_ollama(user_msg, system_instruction=system_prompt, tools_enabled=True)

    # Update History
    history = session.get('chat_history', [])
    history.append({"role": "user", "text": user_msg})
    if resp and 'response' in resp:
        history.append({"role": "ai", "text": resp['response']})

    return jsonify(resp or {"response": "I'm having trouble analyzing that."})