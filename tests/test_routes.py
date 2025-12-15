import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from io import BytesIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Resolved imports: Import app instance and in-memory stores from app.py
from app import app
from services.user_store import users, password_reset_tokens
from utils import sessions

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clear sessions and user data to ensure test isolation
        sessions.clear()
        users.clear()
        password_reset_tokens.clear()

    @patch('routes.health_routes.query_ollama')
    def test_init_context_no_file(self, mock_query):
        response = self.app.post('/init_context')
        self.assertEqual(response.status_code, 400)
        self.assertIn("No file", response.get_json()['error'])

    # @patch('routes.main_routes.query_ollama')
    # def test_init_context_invalid_extension(self, mock_query):
    #     file_content = b"fake"
    #     file = (BytesIO(file_content), 'test.txt')
    #     response = self.app.post('/init_context', data={'file': file, 'token': 't'}, content_type='multipart/form-data')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("Invalid file type", response.get_json()['error'])

    @patch('routes.health_routes.query_ollama')
    @patch('services.pdf_service.pdfplumber.open')
    def test_init_context_success(self, mock_pdf_open, mock_query):
        # Mock PDF
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Bloodwork data..."
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        # Mock AI response
        mock_query.return_value = {
            "summary": "Healthy",
            "issues": [], # Added this to pass the check
            "strategies": [{"name": "Gen", "desc": "Good"}]
        }

        file_content = b"%PDF-1.4..."
        file = (BytesIO(file_content), 'test.pdf')

        response = self.app.post('/init_context', data={'file': file, 'token': 'testtoken'}, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['summary'], "Healthy")

        # Verify session updated
        self.assertIn('testtoken', sessions)
        self.assertEqual(sessions['testtoken']['blood_context']['summary'], "Healthy")

    @patch('routes.meal_routes.query_ollama')
    def test_generate_week(self, mock_query):
        mock_query.return_value = [{"day": "Mon", "meals": [{"title": "Meal"}]}]

        sessions['testtoken'] = {'blood_context': {}}

        response = self.app.post('/generate_week', json={
            'token': 'testtoken',
            'strategy_name': 'Keto',
            'preferences': 'None'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]['meals'][0]['title'], "Meal")

    @patch('routes.meal_routes.query_ollama')
    def test_generate_week_fallback(self, mock_query):
        mock_query.return_value = None # Fail

        sessions['testtoken'] = {'blood_context': {}}

        response = self.app.post('/generate_week', json={
            'token': 'testtoken',
            'strategy_name': 'Keto'
        })

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        # Check first meal of first day
        self.assertEqual(data[0]['meals'][0]['benefit'], "Sustained Energy")

    @patch('routes.health_routes.query_ollama')
    def test_chat_agent(self, mock_query):
        mock_query.return_value = {"response": "Hello"}
        sessions['testtoken'] = {'weekly_plan': [], 'chat_history': []}

        response = self.app.post('/chat_agent', json={
            'token': 'testtoken',
            'message': 'Hi'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['response'], "Hello")

        # Verify history updated
        history = sessions['testtoken']['chat_history']
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['text'], 'Hi')
        self.assertEqual(history[1]['text'], 'Hello')

    @patch('routes.meal_routes.query_ollama')
    def test_get_recipe(self, mock_query):
        mock_query.return_value = {"prep_time": "15m"}

        response = self.app.post('/get_recipe', json={
            'meal_title': 'Steak'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['prep_time'], "15m")

    def test_forgot_password(self):
        users['test@test.com'] = {'password': 'password'}
        response = self.app.post('/forgot-password', data={'email': 'test@test.com'})
        self.assertEqual(response.status_code, 302)
        # Check if email is in one of the values (which are now dicts)
        found = False
        for token, data in password_reset_tokens.items():
            if isinstance(data, dict) and data.get('email') == 'test@test.com':
                found = True
                break
        self.assertTrue(found)

    def test_reset_password(self):
        token = 'test-token'
        # Mock token structure with expiration
        import time
        password_reset_tokens[token] = {
            'email': 'test@test.com',
            'expires': time.time() + 3600
        }
        users['test@test.com'] = {'password': 'old_password'}

        response = self.app.post(f'/reset-password/{token}', data={
            'password': 'new_password',
            'confirm_password': 'new_password'
        })
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(token, password_reset_tokens)

if __name__ == '__main__':
    unittest.main()