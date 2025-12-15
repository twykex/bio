import unittest
from unittest.mock import patch, MagicMock
from services.ai_service import query_ollama
import json

class TestAIService(unittest.TestCase):

    @patch('services.ai_service.requests.post')
    def test_query_ollama_system_instruction_persistence(self, mock_post):
        # 1. First call: Return a tool call
        # 2. Second call: Return a final JSON answer

        # Setup mock responses
        response1 = MagicMock()
        response1.status_code = 200
        # The content must be a JSON string inside the 'message' content
        response1.json.return_value = {
            "message": {
                "content": json.dumps({
                    "tool": "calculate_bmi",
                    "args": {"weight_kg": 70, "height_m": 1.75}
                })
            }
        }

        response2 = MagicMock()
        response2.status_code = 200
        response2.json.return_value = {
            "message": {
                "content": json.dumps({
                    "bmi": 22.86,
                    "status": "Normal"
                })
            }
        }

        mock_post.side_effect = [response1, response2]

        original_system_instruction = "You are a Specific Expert."

        # Call the function
        # tools_enabled=True is required to trigger the tool logic
        result = query_ollama("Calculate my BMI", system_instruction=original_system_instruction, tools_enabled=True)

        # Check calls
        self.assertEqual(mock_post.call_count, 2)

        # Check first call arguments
        args1, kwargs1 = mock_post.call_args_list[0]
        payload1 = kwargs1['json']
        messages1 = payload1['messages']
        # messages[0] is system, messages[1] is user
        self.assertEqual(messages1[0]['role'], 'system')
        self.assertEqual(messages1[0]['content'], original_system_instruction)

        # Check second call arguments (the recursive one)
        args2, kwargs2 = mock_post.call_args_list[1]
        payload2 = kwargs2['json']
        messages2 = payload2['messages']
        self.assertEqual(messages2[0]['role'], 'system')

        # THIS ASSERTION SHOULD FAIL IF BUG EXISTS
        print(f"DEBUG: Second call system instruction: {messages2[0]['content']}")
        self.assertEqual(messages2[0]['content'], original_system_instruction, "System instruction was lost in recursive call!")

if __name__ == '__main__':
    unittest.main()
