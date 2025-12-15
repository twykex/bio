import unittest
from unittest.mock import patch, MagicMock
from services.ai_service import stream_ollama
import json

class TestStreamOllama(unittest.TestCase):

    @patch('services.ai_service.requests.post')
    def test_stream_ollama_normal_text(self, mock_post):
        # Mock a streaming response
        response = MagicMock()
        response.status_code = 200

        # Generator for iter_lines
        def generate_lines():
            chunks = ["Hello", " world", "."]
            for c in chunks:
                yield json.dumps({"message": {"content": c}}).encode('utf-8')

        response.iter_lines = generate_lines
        response.__enter__.return_value = response
        response.__exit__.return_value = None

        mock_post.return_value = response

        # Test
        result = list(stream_ollama([], temperature=0.1))
        # Logic buffers first 10 chars, so "Hello" and " world" are combined
        self.assertEqual(result, ["Hello world", "."])

    @patch('services.ai_service.requests.post')
    def test_stream_ollama_tool_call(self, mock_post):
        # Mock a tool call response
        # It starts with {

        response = MagicMock()
        response.status_code = 200

        tool_json = {
            "tool": "calculate_bmi",
            "args": {"weight_kg": 70, "height_m": 1.75}
        }
        json_str = json.dumps(tool_json)

        # Split json_str into chunks
        def generate_lines():
            # Trigger tool detection
            yield json.dumps({"message": {"content": "{"}}).encode('utf-8')
            yield json.dumps({"message": {"content": json_str[1:]}}).encode('utf-8')

        response.iter_lines = generate_lines
        response.__enter__.return_value = response
        response.__exit__.return_value = None

        mock_post.return_value = response

        # Test
        result = list(stream_ollama([], temperature=0.1))
        # Expectation: "✅ Analysis: BMI: 22.86"
        # because execute_tool_call will be called.

        self.assertTrue(len(result) == 1)
        self.assertIn("✅ Analysis:", result[0])
        self.assertIn("BMI: 22.86", result[0])

    @patch('services.ai_service.requests.post')
    def test_stream_ollama_false_positive_tool(self, mock_post):
        # Starts with { but is not a valid tool call

        response = MagicMock()
        response.status_code = 200

        def generate_lines():
            yield json.dumps({"message": {"content": "{"}}).encode('utf-8')
            yield json.dumps({"message": {"content": "Subject}: Hi"}}).encode('utf-8')

        response.iter_lines = generate_lines
        response.__enter__.return_value = response
        response.__exit__.return_value = None

        mock_post.return_value = response

        # Test
        result = list(stream_ollama([], temperature=0.1))
        # It should buffer and then return the raw text because tool parsing fails
        combined = "".join(result)
        self.assertEqual(combined, "{Subject}: Hi")

if __name__ == '__main__':
    unittest.main()
