import requests
import json
import sys

# CONFIGURATION
MODEL = "gemma3:4b"  # The model you are using
BASE_URL = "http://127.0.0.1:11434"

print(f"🔍 DIAGNOSTIC TOOL: Testing {MODEL} at {BASE_URL}...\n")


def test_connection():
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            print("✅ CONNECTION: Ollama is running.")
            return True
        else:
            print(f"❌ CONNECTION: Failed with status {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ CONNECTION: Critical Error - {e}")
        return False


def test_model_exists():
    try:
        r = requests.get(f"{BASE_URL}/api/tags")
        models = [m['name'] for m in r.json()['models']]
        print(f"📋 AVAILABLE MODELS: {models}")

        if MODEL in models or f"{MODEL}:latest" in models:
            print(f"✅ MODEL CHECK: '{MODEL}' is installed.")
            return True
        else:
            print(f"❌ MODEL CHECK: '{MODEL}' NOT FOUND. Please run: ollama pull {MODEL}")
            return False
    except:
        print("❌ MODEL CHECK: Could not retrieve tags.")
        return False


def test_json_generation():
    print(f"\n🧠 TESTING GENERATION (JSON Mode)...")

    prompt = "List 3 fruits. Format: JSON { 'fruits': [] }"

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",
        "stream": False
    }

    try:
        r = requests.post(f"{BASE_URL}/api/chat", json=payload)
        response = r.json()

        if 'error' in response:
            print(f"❌ AI ERROR: {response['error']}")
            return

        content = response.get('message', {}).get('content', '')
        print(f"📝 RAW OUTPUT: {content}")

        try:
            data = json.loads(content)
            print("✅ JSON PARSE: Success!")
            print(json.dumps(data, indent=2))
        except:
            print("❌ JSON PARSE: Failed. The model outputted invalid JSON.")

    except Exception as e:
        print(f"❌ GENERATION ERROR: {e}")


def test_embeddings():
    print(f"\n📐 TESTING EMBEDDINGS...")
    try:
        r = requests.post(f"{BASE_URL}/api/embeddings", json={
            "model": MODEL,
            "prompt": "Test sentence"
        })
        emb = r.json().get('embedding')
        if emb and len(emb) > 0:
            print(f"✅ EMBEDDINGS: Success! Vector length: {len(emb)}")
        else:
            print(f"❌ EMBEDDINGS: Returned empty.")
            print(r.text)
    except Exception as e:
        print(f"❌ EMBEDDINGS ERROR: {e}")


if __name__ == "__main__":
    if test_connection():
        if test_model_exists():
            test_json_generation()
            test_embeddings()