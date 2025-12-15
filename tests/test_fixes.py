import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from io import BytesIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from services.user_store import users
from services.session_service import sessions
from services.ai_service import query_ollama

class TestBugs(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        sessions.clear()

    @patch('routes.health_routes.advanced_pdf_parse')
    @patch('routes.health_routes.get_embedding')
    @patch('routes.health_routes.query_ollama')
    def test_shared_session_bug_fixed(self, mock_query, mock_embed, mock_parse):
        # This test now verifies the fix

        # Setup mocks
        mock_parse.return_value = ("Content", ["Chunk1"])
        mock_embed.return_value = [0.1, 0.2]
        mock_query.return_value = {"summary": "User A Data", "issues": []}

        # Request 1: User A uploads file without token
        file_a = (BytesIO(b"User A PDF"), 'user_a.pdf')
        # Simulate missing token by not sending it
        response = self.app.post('/init_context', data={'file': file_a}, content_type='multipart/form-data')

        # Verify 400 Bad Request
        self.assertEqual(response.status_code, 400)
        self.assertIn("Token is required", response.get_json()['error'])

        # Verify no None session created
        self.assertNotIn(None, sessions)

    @patch('services.ai_service.requests.post')
    def test_query_ollama_crash_fixed(self, mock_post):
        # Simulate 500 Internal Server Error with HTML body
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "<html><body>Internal Server Error</body></html>"
        # json() method raises JSONDecodeError when content is not JSON
        mock_response.json.side_effect = Exception("Expecting value: line 1 column 1 (char 0)")
        mock_post.return_value = mock_response

        # This should return None gracefully and NOT raise exception
        result = query_ollama("test prompt")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
