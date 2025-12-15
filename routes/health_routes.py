import logging
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER
from utils import get_session, query_ollama, retrieve_relevant_context, get_embedding, analyze_image
from services.pdf_service import advanced_pdf_parse

logger = logging.getLogger(__name__)
health_bp = Blueprint('health_bp', __name__)

@health_bp.route('/init_context', methods=['POST'])
def init_context():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    token = request.form.get('token')

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    text, chunks = advanced_pdf_parse(filepath)
    safe_chunks = chunks[:60]
    embeddings = [get_embedding(chunk) for chunk in safe_chunks]

    user_session = get_session(token)
    user_session['raw_text_chunks'] = safe_chunks
    user_session['embeddings'] = embeddings

    system_prompt = "You are a Functional Doctor. Diagnose the user. Return strict JSON."
    user_prompt = f"""
    DATA: {text[:8000]}

    TASK: Identify the top 3 health issues from this bloodwork.
    For each issue, provide 2 distinct ways to fix it (e.g., Diet vs. Lifestyle).

    OUTPUT JSON FORMAT:
    {{
        "patient_name": "User",
        "health_score": 78,
        "summary": "Short overall health summary.",
        "biomarkers": [
            {{ "name": "Vitamin D", "value": "18", "unit": "ng/mL", "status": "Low" }},
            {{ "name": "Hemoglobin", "value": "14.5", "unit": "g/dL", "status": "Normal" }}
        ],
        "issues": [
            {{
                "title": "Low Vitamin D",
                "severity": "High",
                "value": "18 ng/mL",
                "explanation": "This explains your low energy and weak immunity.",
                "options": [
                    {{ "type": "Dietary", "text": "Eat fatty fish & fortified foods." }},
                    {{ "type": "Lifestyle", "text": "20 mins morning sun exposure." }}
                ]
            }}
        ]
    }}
    """

    data = query_ollama(user_prompt, system_instruction=system_prompt, temperature=0.1)

    if not data or 'issues' not in data:
        data = {
            "patient_name": "Guest",
            "health_score": 75,
            "summary": "We detected some potential optimizations for your metabolism.",
            "biomarkers": [
                {"name": "Glucose", "value": "95", "unit": "mg/dL", "status": "Normal"},
                {"name": "HbA1c", "value": "5.7", "unit": "%", "status": "Borderline"},
                {"name": "Cholesterol", "value": "190", "unit": "mg/dL", "status": "Normal"},
                {"name": "Vitamin D", "value": "30", "unit": "ng/mL", "status": "Normal"}
            ],
            "strategies": [
                {"name": "Metabolic Reset", "desc": "Focus on insulin sensitivity and inflammation reduction."},
                {"name": "Energy Optimization", "desc": "Targeting mitochondrial health and fatigue."},
                {"name": "Balanced Approach", "desc": "Sustainable lifestyle changes for long term health."}
            ],
            "issues": [
                {
                    "title": "Metabolic Efficiency",
                    "severity": "Medium",
                    "value": "Sub-optimal",
                    "explanation": "Your markers suggest insulin resistance risk.",
                    "options": [{"type": "Diet", "text": "Low Carb Protocol"},
                                {"type": "Activity", "text": "Zone 2 Cardio"}]
                },
                {
                    "title": "Inflammation Levels",
                    "severity": "Low",
                    "value": "Elevated",
                    "explanation": "Slightly high CRP indicates stress on the body.",
                    "options": [{"type": "Diet", "text": "Anti-Inflammatory Foods"},
                                {"type": "Supplement", "text": "Omega-3 Protocol"}]
                }
            ]
        }

    user_session["blood_context"] = data
    return jsonify(data)


@health_bp.route('/chat_agent', methods=['POST'])
def chat_agent():
    data = request.json
    user_session = get_session(data.get('token'))
    user_msg = data.get('message')

    rag_context = retrieve_relevant_context(user_session, user_msg)
    summary = user_session.get('blood_context', {}).get('summary', 'No data.')

    system_prompt = f"""
    Medical Assistant.
    CONTEXT: {summary}
    EVIDENCE: {rag_context}
    If user asks for BMI/Calories calculation, output JSON: {{ "tool": "calculate_bmi", ... }}
    Otherwise output JSON: {{ "response": "Your answer..." }}
    """

    resp = query_ollama(user_msg, system_instruction=system_prompt, tools_enabled=True)

    history = user_session.get('chat_history', [])
    history.append({"role": "user", "text": user_msg})
    if resp and 'response' in resp:
        history.append({"role": "ai", "text": resp['response']})

    return jsonify(resp or {"response": "I'm having trouble analyzing that."})


@health_bp.route('/load_demo_data', methods=['POST'])
def load_demo_data():
    token = request.json.get('token')

    sample_context = {
        "patient_name": "Demo User",
        "health_score": 72,
        "summary": "Analysis indicates suboptimal iron levels and elevated cortisol. Metabolic function is otherwise normal. Recommended protocol focuses on stress reduction and nutrient density.",
        "biomarkers": [
            {"name": "Vitamin D", "value": "28", "unit": "ng/mL", "status": "Low"},
            {"name": "Ferritin", "value": "30", "unit": "ng/mL", "status": "Borderline"},
            {"name": "Cortisol", "value": "22", "unit": "ug/dL", "status": "High"},
            {"name": "HbA1c", "value": "5.1", "unit": "%", "status": "Optimal"},
            {"name": "Testosterone", "value": "650", "unit": "ng/dL", "status": "Normal"}
        ],
        "issues": [
            {"title": "Low Iron Stores",
             "explanation": "Ferritin is on the lower end, suggesting reduced iron reserves which may impact energy.",
             "value": "Borderline", "options": [{"text": "Dietary Approach", "type": "Diet"},
                                                 {"text": "Supplementation", "type": "Sup"}]},
            {"title": "Elevated Cortisol",
             "explanation": "High stress hormone levels detected. This can interfere with sleep and recovery.",
             "value": "High", "options": [{"text": "Lifestyle Changes", "type": "Life"},
                                          {"text": "Adaptogens", "type": "Sup"}]}
        ],
        "strategies": [
            {"name": "Adrenal Support", "desc": "Focus on lowering cortisol through adaptogens and nutrient timing."},
            {"name": "Energy Restoration",
             "desc": "High iron bioavailability diet to boost ferritin and oxygen transport."},
            {"name": "Balanced Optimization", "desc": "A moderate approach addressing all biomarkers equally."}
        ]
    }

    user_session = get_session(token)
    user_session['blood_context'] = sample_context

    return jsonify(sample_context)


@health_bp.route('/analyze_food_plate', methods=['POST'])
def analyze_food_plate():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']

    prompt = """
    TASK: Analyze this food image.
    Identify the meal and estimate macros.
    OUTPUT JSON ONLY:
    {
        "meal_name": "Grilled Salmon",
        "ingredients": ["Salmon", "Asparagus", "Rice"],
        "macros": { "calories": 450, "protein": "40g", "carbs": "30g", "fats": "15g" },
        "health_score": 85
    }
    """

    result = analyze_image(file, prompt)

    if not result:
        # Fallback Mock for Demo/Dev
        result = {
            "meal_name": "Detected Meal",
            "ingredients": ["Protein Source", "Vegetables", "Carb Source"],
            "macros": { "calories": 500, "protein": "30g", "carbs": "40g", "fats": "20g" },
            "health_score": 80
        }

    return jsonify(result)


@health_bp.route('/generate_supplement_stack', methods=['POST'])
def generate_supplement_stack():
    data = request.json
    user_session = get_session(data.get('token'))
    current_meds = data.get('current_meds', [])
    summary = user_session.get('blood_context', {}).get('summary', 'General Health')

    prompt = f"""
    ROLE: Clinical Pharmacist & Functional Doctor.
    PATIENT SUMMARY: {summary}
    CURRENT MEDS/SUPPS: {", ".join(current_meds) if current_meds else "None"}

    TASK: Design a supplement stack.
    1. Address the patient's issues.
    2. CHECK FOR INTERACTIONS with current meds.

    OUTPUT JSON ONLY:
    {{
        "stack": [
            {{ "name": "Magnesium Glycinate", "dosage": "400mg", "reason": "Sleep & Anxiety", "interaction_warning": "None" }}
        ],
        "warnings": "Avoid taking Magnesium with antibiotic X."
    }}
    """

    stack = query_ollama(prompt, system_instruction="Return JSON Only.", temperature=0.2)

    if not stack:
        stack = {
            "stack": [
                { "name": "Vitamin D3 + K2", "dosage": "5000 IU", "reason": "Immune Support", "interaction_warning": "None" },
                { "name": "Omega-3", "dosage": "2g", "reason": "Inflammation", "interaction_warning": "Check blood thinners" }
            ],
            "warnings": "Always consult your doctor."
        }

    return jsonify(stack)
