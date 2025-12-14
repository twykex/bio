# BioFlow: AI-Architected Precision Nutrition

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![Flask](https://img.shields.io/badge/framework-Flask-green.svg)
![Ollama](https://img.shields.io/badge/AI-Ollama%20Local-purple.svg)

**BioFlow** is a local, privacy-first biological interface that transforms raw bloodwork data into actionable nutrition protocols. Using advanced local LLMs (Large Language Models), it acts as a "Bio-Architect," analyzing biomarkers to generate optimizing health strategies, 7-day meal plans, recipes, and shopping logistics without sending sensitive medical data to the cloud.

---

## 📸 Interface

*(Add screenshots of your Dashboard here)*
> **BioFlow** features a premium, "Apple Health-inspired" UI with glassmorphism, fluid animations, and a dark-mode-first aesthetic.

---

## ✨ Key Features

### 🧬 Biological Analysis
* **PDF Parsing:** Extracts text from bloodwork/panel PDFs using `pdfplumber`.
* **Contextual Intelligence:** The AI identifies deficiencies (e.g., Vitamin D, Iron) and hormonal imbalances, suggesting specific health strategies (e.g., "Metabolic Reset", "Anti-Inflammatory").

### 🥗 Dynamic Protocol Generation
* **Strategy-Based Meal Planning:** Generates a 7-day dinner protocol tailored specifically to the selected health strategy.
* **Recipe Architect:** Provides detailed macros, cooking steps, and bio-hacking tips for every generated meal.
* **Smart Logistics:** Automatically aggregates ingredients from the weekly plan into a categorized shopping list (Produce, Meat, Pantry).

### 🤖 The "Bio-Architect" Assistant
* **Context-Aware Chat:** A RAG-like (Retrieval-Augmented Generation) chat interface. The AI "knows" your uploaded bloodwork and current meal plan.
* **Ingredient Swapping:** Don't like an ingredient? Ask the Architect to swap it based on your biological needs.

### ⚡ Bio-Hacks (20 Mini-Features)
* **Instant Nutritional Tools:** 20 specialized micro-tools powered by AI.
* **Features Include:** Supplement Advisor, Interaction Checker, Flavor Pairer, Mood Food, Sleep Aid, and more.
* **Robust Fallbacks:** Even if the AI is offline, these tools provide useful default recommendations.

### 🛡️ Robust Backend Engineering
* **Self-Healing JSON Parser:** Custom logic detects and repairs broken JSON output from LLMs (missing brackets, rogue quotes, lazy key generation).
* **Retry Logic:** Automatically retries prompts if the AI output fails validation.
* **Privacy First:** All processing happens locally on your machine via Ollama. No data leaves your network.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML5, TailwindCSS, Alpine.js
* **AI Engine:** Ollama (Local Inference)
* **PDF Processing:** pdfplumber
* **Model Used:** `huihui_ai/gemma3-abliterated:12b` (Configurable)

---

## 🚀 Installation & Setup

### Prerequisites
1.  **Python 3.10+** installed.
2.  **Ollama** installed and running. [Download Ollama](https://ollama.com).
3.  **Hardware:** A GPU with at least 8GB VRAM is recommended. (Tested on RTX 5080).

### 1. Clone the Repository
```bash
git clone [https://github.com/twykex/bio.git](https://github.com/twykex/bio.git)
cd bio
2. Set up Virtual Environment
Bash

# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
Bash

pip install -r requirements.txt
(If requirements.txt is missing, install manually: pip install flask requests pdfplumber)

4. Pull the AI Model
By default, the app uses a specific Gemma 3 model. Run this in your terminal:

Bash

ollama pull huihui_ai/gemma3-abliterated:12b
Note: You can change the model in app.py by editing the OLLAMA_MODEL variable.

🖥️ Usage
Start Ollama: Ensure Ollama is running in the background.

Bash

ollama serve
Run the Application:

Bash

python app.py
Access the Interface: Open your browser and navigate to: http://127.0.0.1:5000

Workflow:

Upload: Drag & drop a PDF (e.g., bloodwork or a dummy PDF text file).

Select Strategy: Choose one of the 3 AI-recommended health paths.

Generate: Watch the AI build your weekly protocol.

Interact: Click meals for recipes, generate a shopping list, or open the "Assistant" drawer to chat.

📂 Project Structure
Plaintext

bio/
├── app.py                  # Core Flask backend & AI logic
├── requirements.txt        # Python dependencies
├── uploads/                # Temp storage for analyzed PDFs
├── templates/
│   └── index.html          # Single-page Application (Frontend)
└── README.md               # Documentation
🔧 Troubleshooting
Issue: "JSON PARSE ERROR" or Blank Screen

Cause: The LLM outputted malformed data.

Solution: The app has built-in "Self-Healing" logic. Check the terminal console. If it persists, try generating again. The AI sometimes needs a second try.

Issue: "Connection Refused"

Cause: Ollama is not running.

Solution: Open a terminal and run ollama serve.

Issue: "Model not found"

Cause: You haven't downloaded the specific model in app.py.

Solution: Run ollama list to see what you have, and update OLLAMA_MODEL in app.py to match a model you have installed (e.g., llama3).

🤝 Contributing
Contributions are welcome!

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
Distributed under the MIT License. See LICENSE for more information.

<p align="center"> Built with ❤️ by twykex </p>


### Steps to complete your repo:

1.  Create a file named `README.md` in your folder.
2.  Paste the code above into it.
3.  (Optional) Take a screenshot of your beautiful new UI, save it as `screenshot.png`, add it to your folder, and uncomment the image link in the "Interface" section.
4.  Run `git add README.md` and `git push` to send it to GitHub.