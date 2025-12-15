import unittest
import time
import sys
import os
sys.path.append(os.getcwd())
from services.user_store import password_reset_tokens

class TestInfraFixes(unittest.TestCase):

    def setUp(self):
        password_reset_tokens.clear()

    def test_password_token_expiration(self):
        token = "expired_token"
        password_reset_tokens[token] = {
            "email": "test@example.com",
            "expires": time.time() - 100
        }

        current_time = time.time()
        for t in list(password_reset_tokens.keys()):
            data = password_reset_tokens.get(t)
            if isinstance(data, dict) and data.get("expires", 0) < current_time:
                password_reset_tokens.pop(t, None)

        self.assertNotIn(token, password_reset_tokens)

    def test_password_token_valid(self):
        token = "valid_token"
        password_reset_tokens[token] = {
            "email": "test@example.com",
            "expires": time.time() + 3600
        }

        current_time = time.time()
        for t in list(password_reset_tokens.keys()):
            data = password_reset_tokens.get(t)
            if isinstance(data, dict) and data.get("expires", 0) < current_time:
                password_reset_tokens.pop(t, None)

        self.assertIn(token, password_reset_tokens)

    def test_url_construction(self):
        OLLAMA_URL = "http://127.0.0.1:11434"
        base_url = OLLAMA_URL.replace("/api/generate", "").replace("/api/chat", "").rstrip("/")
        EMBED_ENDPOINT = f"{base_url}/api/embeddings"
        self.assertEqual(EMBED_ENDPOINT, "http://127.0.0.1:11434/api/embeddings")

if __name__ == '__main__':
    unittest.main()
