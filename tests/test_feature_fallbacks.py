import unittest
from unittest.mock import patch
import json
from app import app

class TestFeatureFallbacks(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.query_ollama')
    def test_fallbacks(self, mock_query):
        # Mock query_ollama to return None, triggering fallback
        mock_query.return_value = None

        features = [
            ('/suggest_supplement', {'focus': 'energy'}, "supplements"),
            ('/check_food_interaction', {'item1': 'a', 'item2': 'b'}, "interaction"),
            ('/recipe_variation', {'recipe': 'a', 'type': 'b'}, "recipe"),
            ('/flavor_pairing', {'ingredient': 'a'}, "pairings"),
            ('/quick_snack', {'preference': 'a'}, "snack"),
            ('/hydration_tip', {'activity': 'run'}, "tip"),
            ('/mood_food', {'mood': 'happy'}, "food"),
            ('/energy_booster', {'context': 'work'}, "food"),
            ('/recovery_meal', {'workout': 'gym'}, "meal"),
            ('/sleep_aid', {'issue': 'none'}, "recommendation"),
            ('/digestive_aid', {'symptom': 'pain'}, "food"),
            ('/immunity_booster', {'season': 'cold'}, "foods"),
            ('/anti_inflammatory', {'condition': 'pain'}, "foods"),
            ('/antioxidant_rich', {'preference': 'fruit'}, "foods"),
            ('/low_gi_option', {'food': 'sugar'}, "alternative"),
            ('/high_protein_option', {'food': 'rice'}, "alternative"),
            ('/fiber_rich_option', {'food': 'bread'}, "alternative"),
            ('/seasonal_swap', {'ingredient': 'tomato', 'season': 'winter'}, "swap"),
            ('/budget_swap', {'ingredient': 'steak'}, "swap"),
            ('/leftover_idea', {'food': 'chicken'}, "idea"),
        ]

        for route, data, expected_key in features:
            response = self.app.post(route, json=data)
            self.assertEqual(response.status_code, 200, f"Failed on {route}")
            json_data = response.json
            self.assertIn(expected_key, json_data, f"Key '{expected_key}' missing in fallback for {route}")

            # Additional check to ensure it's not empty/None
            value = json_data[expected_key]
            self.assertTrue(value, f"Fallback value for {expected_key} in {route} is empty/falsy: {value}")

if __name__ == '__main__':
    unittest.main()
