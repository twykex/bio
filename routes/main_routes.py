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
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            full_text += text + "\n"
            # Chunking by paragraphs (approximate)
            page_chunks = [c.strip() for c in text.split('\n\n') if len(c) > 50]
            chunks.extend(page_chunks)
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

    # 2. Vector Embeddings (RAG Setup)
    embeddings = [get_embedding(chunk) for chunk in chunks]

    session = get_session(token)
    session['raw_text_chunks'] = chunks
    session['embeddings'] = embeddings

    # 3. FEW-SHOT PROMPTING (Teaching by Example)
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
    STRUCTURE: {{ "patient_summary": "...", "flagged_biomarkers": [ ... ], "strategies": [ ... ] }}
    """

    data = query_ollama(user_prompt, system_instruction=system_prompt, temperature=0.1)

    if not data:
        data = {"patient_summary": "Analysis failed.", "flagged_biomarkers": [], "strategies": []}

    session["blood_context"] = data
    return jsonify(data)


@main_bp.route('/generate_week', methods=['POST'])
def generate_week():
    data = request.json
    session = get_session(data.get('token'))
    summary = session.get('blood_context', {}).get('patient_summary', '')
    strategy = data.get('strategy_name', 'General')

    prompt = f"Plan 7 dinners for: {summary}. Focus: {strategy}. Format: JSON Array [{{'day':'Mon', 'title':'...', 'ingredients':['...'], 'benefit':'...'}}]"

    plan = query_ollama(prompt, system_instruction="You are a Nutritionist.", temperature=0.5)
    return jsonify(plan or [])


@main_bp.route('/chat_agent', methods=['POST'])
def chat_agent():
    data = request.json
    session = get_session(data.get('token'))
    user_msg = data.get('message')

    # 1. RAG SEARCH: Find specific lines in the PDF
    rag_context = retrieve_relevant_context(session, user_msg)

    # 2. GLOBAL CONTEXT
    summary = session.get('blood_context', {}).get('patient_summary', 'No data.')

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