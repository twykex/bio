### FILENAME: debug_ollama.py ###
import requests
import json

CHAT_MODEL = "gemma3:4b"
EMBED_MODEL = "nomic-embed-text"
BASE_URL = "http://127.0.0.1:11434"

print(f"🔍 TESTING HYBRID ARCHITECTURE...")
print(f"🗣️  Chat Model: {CHAT_MODEL}")
print(f"🧠 Memory Model: {EMBED_MODEL}")

def test_chat():
    print(f"\n1. Testing Chat ({CHAT_MODEL})...")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={
            "model": CHAT_MODEL,
            "messages": [{"role":"user", "content":"say hello in json { 'msg': 'hello' }"}],
            "format": "json",
            "stream": False
        })
        print("✅ Chat Response:", r.json()['message']['content'])
    except Exception as e:
        print("❌ Chat Failed:", e)

def test_embed():
    print(f"\n2. Testing Embeddings ({EMBED_MODEL})...")
    try:
        r = requests.post(f"{BASE_URL}/api/embeddings", json={
            "model": EMBED_MODEL,
            "prompt": "Medical data"
        })
        if 'embedding' in r.json():
            print(f"✅ Embeddings Working! Vector Size: {len(r.json()['embedding'])}")
        else:
            print("❌ Embeddings Failed:", r.text)
    except Exception as e:
        print("❌ Connection Failed:", e)

if __name__ == "__main__":
    test_chat()
    test_embed()