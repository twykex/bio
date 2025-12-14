import requests
import json
import re

# 1. SETUP
MODEL = "huihui_ai/gemma3-abliterated:12b"
URL = "http://localhost:11434/api/generate"

print(f"🧪 Testing Model: {MODEL}")
print("--------------------------------------------------")

# 2. PROMPT
# We are NOT using 'format': 'json' to avoid the crash.
# We are relying on the prompt to force JSON.
prompt = """
You are a Data API. 
TASK: Output a JSON object for a meal.
RULES: 
1. Output JSON ONLY. 
2. Do not say "Here is the JSON".
3. Do not use Markdown blocks.

DATA TO GENERATE:
{
    "meal": "Steak and Eggs",
    "calories": 800
}
"""

payload = {
    "model": MODEL,
    "prompt": prompt,
    "stream": False,
    # "format": "json" <--- DISABLED (This was causing the crash)
}

try:
    # 3. SEND REQUEST
    print("⏳ Sending request to AI...")
    r = requests.post(URL, json=payload)

    if r.status_code == 200:
        raw_response = r.json()['response']

        print("\n📝 RAW AI RESPONSE (Between lines):")
        print("==================================================")
        print(raw_response)
        print("==================================================")

        # 4. TEST PARSING LOGIC
        print("\n⚙️ Testing Parser...")

        # Regex to find the JSON part (in case AI added extra text)
        match = re.search(r'(\{.*\}|\[.*\])', raw_response, re.DOTALL)

        if match:
            clean_text = match.group(0)
            print(f"   Found JSON segment: {clean_text[:50]}...")

            try:
                data = json.loads(clean_text)
                print("\n✅ SUCCESS! valid JSON object detected.")
                print(json.dumps(data, indent=2))
            except Exception as e:
                print(f"\n❌ PARSE ERROR: Found bracket {{ }} but content was invalid JSON.\nError: {e}")
        else:
            print("\n❌ FAILURE: Could not find any { } or [ ] in the response.")

    else:
        print(f"❌ SERVER ERROR: {r.status_code}")
        print(r.text)

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")