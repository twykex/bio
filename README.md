# 🧬 BioFlow AI

> **Decode Your Biology.**  
> An advanced, privacy-focused health intelligence platform that transforms bloodwork data into hyper-personalized nutrition and fitness protocols using local AI agents.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Ollama](https://img.shields.io/badge/AI-Ollama%20Local-orange.svg)

---

## 📖 Overview

**BioFlow AI** is a full-stack health application that bridges the gap between raw medical data and daily lifestyle choices. Unlike generic trackers, BioFlow uses **RAG (Retrieval-Augmented Generation)** to read your actual bloodwork PDFs and constructs a health plan tailored to your specific biomarkers (e.g., Vitamin D levels, Cholesterol, Iron).

It runs **100% locally** on your machine using Ollama, ensuring your sensitive medical data never leaves your computer.

## ✨ Key Features

### 🧠 Advanced AI Architecture
*   **Hybrid Model System:** Uses **Gemma 3 (4B)** for high-speed conversational logic and **Nomic Embed Text** for mathematical vector search (RAG).
*   **Agentic Tool Use:** The AI can execute Python code to calculate BMIs, caloric needs, and macro splits accurately.
*   **Self-Healing JSON:** A custom parser that detects malformed AI output and recursively asks the AI to fix its own syntax errors.

### 🔬 The Bio-Scan Protocol
*   **PDF Analysis:** Upload a blood panel PDF. The system extracts text, chunks it, and creates vector embeddings.
*   **Consultation Mode:** An interactive "Doctor" agent walks you through your top 3 health red flags and asks for your input on how to solve them (e.g., "Dietary fix vs. Supplement fix").

### 🥗 The Nutrition Architect
*   **Smart Strategy Wizard:** The AI proposes 3 distinct meal strategies (e.g., "Aggressive Repair" vs. "Balanced Lifestyle") based on your blood results.
*   **Interactive Calendar:** A drag-and-drop style weekly planner with checkable tasks.
*   **Context-Aware:** Meals are generated based on bio-data + user constraints (Budget, Time, Cuisine).

### 🎨 Next-Gen UI/UX
*   **Glassmorphism 2.0:** A premium, dark-mode aesthetic with fluid animations.
*   **Living UI:** Typewriter chat effects, "breathing" backgrounds, and smart tooltips that define medical terms on hover.

---

## 🛠️ Tech Stack

*   **Backend:** Python, Flask
*   **Frontend:** HTML5, Tailwind CSS (via CDN), Alpine.js (Reactive State)
*   **AI Engine:** Ollama (Local Inference)
*   **Data Processing:** PDFPlumber, Vector Embeddings (Cosine Similarity)

---

## 🚀 Installation & Setup

### 1. Prerequisites
You must have **[Ollama](https://ollama.com/)** installed and running on your machine.

### 2. Download Models
BioFlow requires two specific models to function (one for talking, one for memory). Run these commands in your terminal:

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
3. Clone & Install Dependencies
code
Bash
# Clone the repository
git clone https://github.com/yourusername/bioflow.git
cd bioflow

# Create Virtual Environment (Optional but recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install Python Packages
pip install flask requests pdfplumber werkzeug
4. Run the Application
code
Bash
python app.py
Open your browser and navigate to: http://127.0.0.1:5000
💡 How It Works (The Architecture)
Ingestion: When you upload a PDF, pdfplumber extracts the text.
Vectorization: The nomic-embed-text model converts the text chunks into mathematical vectors (embeddings) and stores them in memory.
Retrieval (RAG): When you ask a question, the system finds the specific paragraphs in your PDF that match your query using Cosine Similarity.
Generation: The gemma3:4b model receives your question + the relevant PDF paragraphs + a System Prompt (e.g., "You are a Functional Doctor").
Validation: If the AI outputs a JSON meal plan, the backend validates the structure. If it's broken, a "Critic Agent" feeds the error back to the AI to auto-correct it.
📂 Project Structure
code
Code
bioflow/
├── app.py                 # Entry point
├── config.py              # Configuration (Ports, Models)
├── utils.py               # The AI Brain (RAG, Embeddings, Tools)
├── routes/
│   ├── main_routes.py     # Core logic (Week Gen, Chat, Consult)
│   └── mini_apps.py       # Bio-Hack Tools (Quick Snack, Sleep Aid)
├── static/
│   ├── css/style.css      # Glassmorphism Styles
│   └── js/app.js          # Alpine.js Frontend Logic
├── templates/
│   └── index.html         # Main Single-Page App
└── uploads/               # Temporary storage for PDFs
🛡️ Privacy Note
Your data never leaves your device.
Unlike ChatGPT or Claude, this application runs entirely on localhost. Your medical PDFs are processed by the Ollama instance running on your own hardware. No API keys are required, and no data is sent to the cloud.
🔮 Future Roadmap

Vision Support: Use llava to read charts/graphs from PDFs directly.

Voice Mode: Add Whisper for voice-to-text consultation.

Wearable Sync: Import Apple Health/Oura Ring data via JSON export.

Database: Move from in-memory session to SQLite for long-term tracking.
Made with ❤️ and Python.
code
Code