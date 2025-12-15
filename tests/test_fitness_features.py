import unittest
from unittest.mock import patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from services.session_service import sessions

class TestFitnessFeatures(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        sessions.clear()

    @patch('routes.workout_routes.query_ollama')
    def test_propose_fitness_strategies(self, mock_query):
        # Mock failure to trigger fallback
        mock_query.return_value = None

        sessions['testtoken'] = {'blood_context': {'summary': 'Healthy'}}

        response = self.app.post('/propose_fitness_strategies', json={
            'token': 'testtoken',
            'lifestyle': {'goal': 'Muscle Gain'}
        })

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['id'], 'build')
        self.assertEqual(data[0]['title'], 'Hypertrophy Protocol')

if __name__ == '__main__':
    unittest.main()
