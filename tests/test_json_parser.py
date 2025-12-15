import sys
import os
sys.path.append(os.getcwd())
import unittest
from services.ai_service import clean_json_output

class TestJsonParser(unittest.TestCase):
    def test_basic_json(self):
        text = 'some text {"key": "value"} trailing'
        expected = '{"key": "value"}'
        self.assertEqual(clean_json_output(text), expected)

    def test_json_with_braces_in_string(self):
        # This currently passes by accident (fallback)
        text = '{"key": "value with { brace"}'
        expected = '{"key": "value with { brace"}'
        self.assertEqual(clean_json_output(text), expected)

    def test_json_with_braces_in_string_and_trailing_garbage(self):
        # This triggers the bug: parser gets confused by inner brace and misses the real end,
        # eventually returning the whole string including garbage.
        text = '{"key": "value with { brace"} trailing garbage'
        expected = '{"key": "value with { brace"}'
        self.assertEqual(clean_json_output(text), expected)

    def test_nested_structure_with_garbage(self):
        text = '{"key": {"nested": "value"}} trailing'
        expected = '{"key": {"nested": "value"}}'
        self.assertEqual(clean_json_output(text), expected)

if __name__ == '__main__':
    unittest.main()
