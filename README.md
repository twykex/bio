# 🧬 BioFlow AI

> **Decode Your Biology. Optimize Your Life.**
> An advanced, privacy-first health intelligence platform that transforms raw bloodwork data into hyper-personalized nutrition, fitness, and lifestyle protocols using **local AI agents**.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Flask](https://img.shields.io/badge/framework-Flask-green.svg)
![Ollama](https://img.shields.io/badge/AI-Ollama%20Local-orange.svg)
![Tailwind](https://img.shields.io/badge/UI-Tailwind%20CSS-cyan.svg)

---

## 📖 Overview

**BioFlow AI** is a "Functional Medicine Doctor in your pocket." It bridges the gap between complex medical data and daily actionable choices. By running **100% locally** on your machine (using Ollama), it ensures your sensitive health data **never** leaves your device.

The system uses a **Retrieval-Augmented Generation (RAG)** architecture to:
1.  **Read** your uploaded bloodwork PDFs.
2.  **Analyze** biomarkers (Vitamin D, Hormones, Lipids, etc.).
3.  **Generate** highly specific meal plans, workout routines, and supplement stacks tailored to *your* biology.

---

## ✨ Key Features

*   **🔒 Privacy-First**: No cloud APIs. No data sharing. Everything runs on localhost.
*   **🧠 Hybrid AI Brain**: Combines `gemma3:4b` for conversational logic with `nomic-embed-text` for semantic vector search (RAG).
*   **🩸 Smart PDF Analysis**: Extracts text from medical reports, chunks it, and creates embeddings for context-aware QA.
*   **🩺 Interactive Consultation**: Chat with a "Doctor" agent that knows your specific blood results.
*   **🥗 Dynamic Nutrition**: Generates 7-day meal plans with macro breakdowns, specifically targeting your deficiencies (e.g., "High Iron" for low Ferritin).
*   **🏋️ Adaptive Fitness**: Creates workout plans based on your energy levels and goals.
*   **🛠️ Bio-Hack Tools**: 20+ mini-apps for specific needs (Sleep Aid, Caffeine Optimizer, Supplement Interaction Checker).
*   **🎨 Glassmorphism UI**: A premium, modern dark-mode interface built with Tailwind CSS and Alpine.js.

---

## 🚀 Installation & Setup

### 1. Prerequisites
You must have **[Ollama](https://ollama.com/)** installed and running.

### 2. Pull Required Models
BioFlow needs two specific models: one for talking, one for memory.
```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

### 3. Clone & Install
```bash
git clone https://github.com/yourusername/bioflow.git
cd bioflow

# Create Virtual Env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 4. Run the App
```bash
python app.py
# Access at: http://127.0.0.1:5000
```

---

## 📂 Codebase Deep Dive

Here is a comprehensive breakdown of **every single code file** in the project, explaining its specific role in the architecture.

### 🏗️ Root Directory

| File | Description |
| :--- | :--- |
| **`app.py`** | **The Brain.** The main entry point for the Flask application. It initializes the app, registers all Blueprints (routes), and starts the server. It also handles port conflict resolution. |
| **`config.py`** | **Settings.** Central configuration file. Defines the AI models to use (`OLLAMA_MODEL`), the embedding model, server port, and upload directories. |
| **`utils.py`** | **The Bridge.** Acts as a central hub for importing/exporting services. Instead of importing from 5 different service files, other parts of the app just import from here. |
| **`server_utils.py`** | **Helpers.** Contains utility functions to find a free network port (so the app doesn't crash if port 5000 is taken) and to auto-open the browser. |
| **`doctor.py`** | **Diagnostic Tool.** A script you can run (`python doctor.py`) to verify that all required files exist, Python syntax is correct, and the environment is healthy. |
| **`debug_ollama.py`** | **Connection Tester.** A standalone script to test if Ollama is running, reachable, and if the models are correctly pulled and responding to JSON requests. |
| **`test_model.py`** | **Prompt Engineering Test.** A script used during development to fine-tune how the AI outputs JSON data, ensuring the parser works correctly. |
| **`requirements.txt`** | **Dependencies.** Lists all Python packages required (Flask, Requests, PDFPlumber, etc.). |
| **`package.json`** | **Frontend Config.** Manages frontend dependencies (like Tailwind CSS) and build scripts. |
| **`tailwind.config.js`** | **Style Config.** Configuration for Tailwind CSS. Defines the custom color palette (`glass`, `brand`), fonts, and animations used in the UI. |

### 🧠 Services (`/services`)
*The "Business Logic" layer. These files handle the heavy lifting.*

| File | Description |
| :--- | :--- |
| **`ai_service.py`** | **The AI Interface.** Manages all communication with Ollama. It handles sending prompts, managing retry logic if the AI fails, and includes the `analyze_image` function for food recognition. |
| **`rag_service.py`** | **The Memory System.** Implements Retrieval-Augmented Generation. It handles `get_embedding` (turning text into numbers) and `cosine_similarity` (finding the most relevant text for a user's question). |
| **`pdf_service.py`** | **The Reader.** Uses `pdfplumber` to extract text from uploaded PDF blood reports. It cleans the text and chunks it into manageable pieces for the AI. |
| **`session_service.py`** | **State Management.** Manages user sessions in memory. It stores the uploaded PDF context, chat history, and generated plans for each user token. |
| **`json_cleaner.py`** | **The Fixer.** A robust utility that repairs broken JSON output from the AI. If the AI misses a bracket or adds a comment, this file uses stack-based parsing to extract the valid JSON object. |
| **`tools.py`** | **Python Tools.** Native Python functions that the AI can "call". Currently includes `calculate_bmi` and `estimate_daily_calories`. |
| **`user_store.py`** | **Data Store.** A simple in-memory dictionary to store user credentials and password reset tokens (since we don't use a database for this local version). |

### 🛣️ Routes (`/routes`)
*The "Controller" layer. These files define the URL endpoints.*

| File | Description |
| :--- | :--- |
| **`auth_routes.py`** | **Authentication.** Handles Login (`/login`), Signup (`/signup`), Guest Access, and Password Reset flows. |
| **`health_routes.py`** | **Core Health.** The heart of the app. Handles PDF upload (`/init_context`), the main Chat Agent (`/chat_agent`), and loading demo data. |
| **`meal_routes.py`** | **Nutrition.** Endpoints for generating weekly meal plans, creating shopping lists, getting single recipes, and proposing dietary strategies. |
| **`workout_routes.py`** | **Fitness.** Endpoints for generating workout schedules and proposing fitness strategies based on user goals and bloodwork. |
| **`mini_apps.py`** | **Tool Handler.** A universal route (`/<action>`) that powers all the small tools (Sleep Aid, etc.). It looks up the config and sends the prompt to the AI. |
| **`mini_apps_config.py`** | **Tool Config.** Defines the "Personality" (System Prompt), "Task" (User Prompt), and "Creativity" (Temperature) for every mini-app (e.g., `caffeine_optimizer`, `stress_relief`). |

### 💾 Data (`/data`)

| File | Description |
| :--- | :--- |
| **`fallbacks.py`** | **Safety Net.** Contains hardcoded Meal Plans and Workout Plans. If the AI service is down or fails to generate valid JSON, the app seamlessly serves this data so the user never sees an error. |

### 🎨 Frontend (`/static` & `/templates`)

*   **`templates/`**: Contains the HTML files.
    *   `index.html`: The main Single Page Application (SPA) shell.
    *   `components/`: Modular HTML parts (Sidebar, Header, Modals).
    *   `components/tabs/`: The different views (Dashboard, Health, Nutrition, Fitness, etc.).
*   **`static/js/app.js`**: The main frontend logic (Alpine.js). Initializes the state, handles routing between tabs, and manages the global data store.
*   **`static/js/modules/`**: The frontend logic is split into modules (`fitness.js`, `nutrition.js`, `charts.js`, etc.) to keep the code clean and maintainable.

---

## 🔮 Future Roadmap

*   [ ] **Voice Mode**: Integration with Whisper for voice-to-text consultations.
*   [ ] **Wearable Sync**: Import data from Apple Health or Oura Ring via JSON export.
*   [ ] **Local Database**: Move from in-memory session storage to SQLite for persistent long-term tracking.
*   [ ] **Vision 2.0**: Better graph reading capabilities from bloodwork PDFs.

---

## 🛡️ Privacy Note

Your health data is sensitive. **BioFlow AI respects that.**
*   **No Cloud Uploads:** Your PDF is processed in RAM on your machine.
*   **Local Inference:** All AI thinking happens on your CPU/GPU.
*   **No Tracking:** We do not collect analytics or user data.

---

Made with ❤️ and Python.
