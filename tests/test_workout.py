import unittest
from unittest.mock import patch
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils import sessions

class TestWorkout(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        sessions.clear()

    @patch('routes.main_routes.query_ollama')
    def test_generate_workout_success(self, mock_query):
        # Mock successful AI response with new structure
        mock_response = [{
            "day": "Mon",
            "focus": "Test Focus",
            "exercises": [
                {"name": "Test Ex", "sets": "3", "reps": "10", "rest": "60s", "tip": "Test Tip"}
            ],
            "benefit": "Test Benefit"
        }]
        mock_query.return_value = mock_response

        sessions['testtoken'] = {}

        response = self.app.post('/generate_workout', json={
            'token': 'testtoken',
            'strategy_name': 'Strength',
            'lifestyle': {}
        })

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(isinstance(data, list))
        self.assertEqual(data[0]['focus'], "Test Focus")
        self.assertEqual(data[0]['exercises'][0]['name'], "Test Ex")
        self.assertEqual(data[0]['exercises'][0]['sets'], "3")

    @patch('routes.main_routes.query_ollama')
    def test_generate_workout_fallback(self, mock_query):
        # Mock failure to trigger fallback
        mock_query.return_value = None

        sessions['testtoken'] = {}

        response = self.app.post('/generate_workout', json={
            'token': 'testtoken',
            'strategy_name': 'Strength',
            'lifestyle': {}
        })

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(isinstance(data, list))

        # Verify fallback structure
        first_day = data[0]
        self.assertIn('exercises', first_day)
        self.assertIn('warmup', first_day)
        self.assertIn('cooldown', first_day)

        first_ex = first_day['exercises'][0]

        # Check new fields
        self.assertIn('name', first_ex)
        self.assertIn('sets', first_ex)
        self.assertIn('reps', first_ex)
        self.assertIn('rest', first_ex)
        self.assertIn('tip', first_ex)
        self.assertIn('rpe', first_ex)

if __name__ == '__main__':
    unittest.main()
