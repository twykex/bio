import unittest
import json
import io
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from flask import session

class TestNewFeatures(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('routes.health_routes.query_ollama')
    def test_generate_supplement_stack(self, mock_query_ollama):
        # Mock Response
        mock_response = {
            "stack": [
                { "name": "Vitamin D", "dosage": "2000 IU", "reason": "Low levels", "interaction_warning": "None" }
            ],
            "warnings": "None"
        }
        mock_query_ollama.return_value = mock_response

        payload = {
            "token": "test_token",
            "current_meds": ["Ibuprofen"]
        }

        response = self.app.post('/generate_supplement_stack',
                                 data=json.dumps(payload),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('stack', data)
        self.assertEqual(len(data['stack']), 1)
        self.assertEqual(data['stack'][0]['name'], "Vitamin D")

    @patch('routes.health_routes.analyze_image')
    def test_analyze_food_plate(self, mock_analyze_image):
        # Mock Response
        mock_response = {
            "meal_name": "Test Meal",
            "ingredients": ["A", "B"],
            "macros": { "calories": 500 },
            "health_score": 90
        }
        mock_analyze_image.return_value = mock_response

        # Create dummy image
        data = {
            'file': (io.BytesIO(b"dummy image data"), 'test.jpg')
        }

        response = self.app.post('/analyze_food_plate', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['meal_name'], "Test Meal")
        mock_analyze_image.assert_called_once()

    @patch('routes.mini_apps.query_ollama')
    def test_check_drug_interaction(self, mock_query_ollama):
        # This tests the mini_app route
        mock_response = {
            "interactions": [
                { "drugs": "A + B", "severity": "High", "effect": "Bad stuff" }
            ]
        }
        mock_query_ollama.return_value = mock_response

        payload = {
            "drug_list": "Aspirin, Warfarin"
        }

        response = self.app.post('/check_drug_interaction',
                                 data=json.dumps(payload),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('interactions', data)
        self.assertEqual(data['interactions'][0]['severity'], "High")

if __name__ == '__main__':
    unittest.main()
