import unittest
from unittest.mock import patch
import json
from app import app

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('routes.features.query_ollama')
    def test_all_features(self, mock_query):
        features = [
            ('/suggest_supplement', {'focus': 'energy'}, {"supplements": []}),
            ('/check_food_interaction', {'item1': 'a', 'item2': 'b'}, {"interaction": "Safe"}),
            ('/recipe_variation', {'recipe': 'a', 'type': 'b'}, {"recipe": "b-a"}),
            ('/flavor_pairing', {'ingredient': 'a'}, {"pairings": []}),
            ('/quick_snack', {'preference': 'a'}, {"snack": "apple"}),
            ('/hydration_tip', {'activity': 'run'}, {"tip": "water"}),
            ('/mood_food', {'mood': 'happy'}, {"food": "cake"}),
            ('/energy_booster', {'context': 'work'}, {"food": "coffee"}),
            ('/recovery_meal', {'workout': 'gym'}, {"meal": "shake"}),
            ('/sleep_aid', {'issue': 'none'}, {"recommendation": "milk"}),
            ('/digestive_aid', {'symptom': 'pain'}, {"food": "tea"}),
            ('/immunity_booster', {'season': 'cold'}, {"foods": []}),
            ('/anti_inflammatory', {'condition': 'pain'}, {"foods": []}),
            ('/antioxidant_rich', {'preference': 'fruit'}, {"foods": []}),
            ('/low_gi_option', {'food': 'sugar'}, {"alternative": "stevia"}),
            ('/high_protein_option', {'food': 'rice'}, {"alternative": "meat"}),
            ('/fiber_rich_option', {'food': 'bread'}, {"alternative": "whole wheat"}),
            ('/seasonal_swap', {'ingredient': 'tomato', 'season': 'winter'}, {"swap": "canned"}),
            ('/budget_swap', {'ingredient': 'steak'}, {"swap": "beans"}),
            ('/leftover_idea', {'food': 'chicken'}, {"idea": "sandwich"}),
        ]

        for route, data, mock_resp in features:
            mock_query.return_value = mock_resp
            response = self.app.post(route, json=data)
            self.assertEqual(response.status_code, 200, f"Failed on {route}")
            self.assertEqual(response.json, mock_resp, f"Response mismatch on {route}")

if __name__ == '__main__':
    unittest.main()
