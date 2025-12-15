import requests
import json

# CONFIGURATION
CHAT_MODEL = "gemma3:4b"  # The "Brain" (Talking)
EMBED_MODEL = "nomic-embed-text"  # The "Memory" (Math)
BASE_URL = "http://127.0.0.1:11434"

print(f"🔍 DIAGNOSTIC: Hybrid AI Architecture Test")
print(f"----------------------------------------")
print(f"🗣️  Chat Model:   {CHAT_MODEL}")
print(f"🧠 Memory Model: {EMBED_MODEL}")
print(f"----------------------------------------\n")


def test_chat_json():
    print(f"1️⃣  TESTING CHAT (JSON Mode)...")
    payload = {
        "model": CHAT_MODEL,
        "messages": [{"role": "user", "content": "List 3 colors. JSON format: { 'colors': [] }"}],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1}  # Strict mode
    }

    try:
        r = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if r.status_code == 200:
            content = r.json()['message']['content']
            print(f"   RAW OUTPUT: {content}")
            try:
                json.loads(content)
                print(f"   ✅ PASS: {CHAT_MODEL} generated valid JSON.")
            except:
                print(f"   ❌ FAIL: {CHAT_MODEL} output invalid JSON.")
        else:
            print(f"   ❌ FAIL: Connection Error {r.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")


def test_embeddings():
    print(f"\n2️⃣  TESTING MEMORY (Embeddings)...")
    payload = {
        "model": EMBED_MODEL,
        "prompt": "The sky is blue."
    }

    try:
        r = requests.post(f"{BASE_URL}/api/embeddings", json=payload)
        if r.status_code == 200:
            embedding = r.json().get('embedding')
            if embedding and len(embedding) > 0:
                print(f"   ✅ PASS: {EMBED_MODEL} created vector (Size: {len(embedding)}).")
            else:
                print(f"   ❌ FAIL: Embedding list is empty.")
        else:
            print(f"   ❌ FAIL: Server returned {r.status_code} - {r.text}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")


if __name__ == "__main__":
    test_chat_json()
    test_embeddings()