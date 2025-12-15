import os
import sys
import py_compile

# --- CONFIGURATION ---
REQUIRED_FILES = [
    "templates/index.html",
    "templates/components/landing.html",
    "templates/components/layout/sidebar.html",
    "templates/components/layout/header.html",
    "templates/components/tabs/dashboard.html",
    "templates/components/tabs/status.html",
    "templates/components/tabs/health.html",
    "templates/components/tabs/nutrition.html",
    "templates/components/tabs/fitness.html",
    "templates/components/tabs/journal.html",
    "templates/components/tabs/biohacks_settings.html",
    "templates/components/modals/chat.html",
    "templates/components/modals/consultation.html",
    "templates/components/modals/meal_modals.html",
    "templates/components/modals/fitness_modals.html",
    "templates/components/modals/biohack_modals.html",
    "static/js/app.js",
    "static/js/modules/config.js",
    "static/js/modules/fitness.js",
    "static/js/modules/nutrition.js",
    "static/js/modules/charts.js",
    "static/js/modules/journal.js",
    "static/js/modules/consultation.js",
    "static/js/modules/utils.js",
]

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
YELLOW = "\033[93m"

def check_structure():
    print(f"\n{YELLOW}--- 1. Checking File Structure ---{RESET}")
    missing = []
    for file_path in REQUIRED_FILES:
        if os.path.exists(file_path):
            print(f"{GREEN}✓ Found:{RESET} {file_path}")
        else:
            print(f"{RED}✗ MISSING:{RESET} {file_path}")
            missing.append(file_path)
    
    if missing:
        print(f"\n{RED}ERROR: You are missing {len(missing)} files. Please go back and create them.{RESET}")
        return False
    return True

def check_html_import():
    print(f"\n{YELLOW}--- 2. Checking HTML Script Tag ---{RESET}")
    try:
        with open("templates/index.html", "r") as f:
            content = f.read()
            if 'type="module"' in content and 'src="/static/js/app.js"' in content:
                print(f"{GREEN}✓ index.html is correctly using ES6 Modules.{RESET}")
            else:
                print(f"{RED}✗ ERROR in index.html:{RESET}")
                print("   Your script tag MUST look like this: <script type=\"module\" src=\"/static/js/app.js\"></script>")
                return False
    except FileNotFoundError:
        print(f"{RED}✗ index.html not found.{RESET}")
        return False
    return True

def check_python_syntax():
    print(f"\n{YELLOW}--- 3. Checking Python Syntax ---{RESET}")
    error_count = 0
    for root, dirs, files in os.walk("."):
        if "__pycache__" in root or ".venv" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py") and file != "doctor.py":
                path = os.path.join(root, file)
                try:
                    py_compile.compile(path, doraise=True)
                    # print(f"{GREEN}✓ Valid:{RESET} {file}")
                except py_compile.PyCompileError:
                    print(f"{RED}✗ SYNTAX ERROR:{RESET} {path}")
                    error_count += 1
                except Exception as e:
                    print(f"{RED}✗ Error checking {path}: {e}{RESET}")
    
    if error_count == 0:
        print(f"{GREEN}✓ All Python files compile successfully.{RESET}")
    else:
        print(f"{RED}✗ Found syntax errors in {error_count} Python files.{RESET}")

def main():
    print(f"{YELLOW}Running BioFlow Project Doctor...{RESET}")
    
    struct_ok = check_structure()
    html_ok = check_html_import()
    check_python_syntax()

    print("\n" + "="*30)
    if struct_ok and html_ok:
        print(f"{GREEN}✅ PROJECT LOOKS GOOD TO GO!{RESET}")
        print(f"Run your app with: {YELLOW}python app.py{RESET}")
    else:
        print(f"{RED}❌ FIX ERRORS ABOVE BEFORE RUNNING.{RESET}")

if __name__ == "__main__":
    main()
