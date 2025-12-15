import unittest
import sys
import os
import json

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_service import repair_lazy_json, fix_truncated_json, clean_and_parse_json

class TestJsonUtils(unittest.TestCase):

    def test_repair_lazy_json_missing_title(self):
        # "day": "Mon", "Meal Name",
        text = '{"day": "Mon", "Salmon", "benefit": "Omega3"}'
        # expected: "day": "Mon", "title": "Salmon", "benefit": "Omega3"
        repaired = repair_lazy_json(text)
        self.assertIn('"title": "Salmon"', repaired)

    def test_repair_lazy_json_missing_desc(self):
        # ,"Some Description"}
        text = '{"name": "Vit D", "Optimize levels"}'
        repaired = repair_lazy_json(text)
        self.assertIn('"desc": "Optimize levels"', repaired)

    def test_fix_truncated_json(self):
        text = '[{"name": "test"'
        repaired = fix_truncated_json(text)
        self.assertEqual(repaired, '[{"name": "test"}]')

        text = '{"data": [1, 2'
        repaired = fix_truncated_json(text)
        self.assertEqual(repaired, '{"data": [1, 2]}')

        text = '{"key": "val'
        repaired = fix_truncated_json(text)
        self.assertEqual(repaired, '{"key": "val"}')

    def test_clean_and_parse_json_markdown(self):
        text = '```json\n{"key": "value"}\n```'
        result = clean_and_parse_json(text)
        self.assertEqual(result, {"key": "value"})

    def test_clean_and_parse_json_extra_text(self):
        text = 'Here is the json: {"key": "value"}'
        result = clean_and_parse_json(text)
        self.assertEqual(result, {"key": "value"})

    def test_clean_and_parse_json_rogue_quotes(self):
        # text = re.sub(r'\]\s*"\s*\}', '] }', text)
        text = '{"list": ["item"]"}'
        result = clean_and_parse_json(text)
        self.assertEqual(result, {"list": ["item"]})

    def test_clean_and_parse_json_trailing_comma(self):
        text = '{"key": "value",}'
        result = clean_and_parse_json(text)
        self.assertEqual(result, {"key": "value"})

        text = '[1, 2, ]'
        result = clean_and_parse_json(text)
        self.assertEqual(result, [1, 2])

    def test_clean_and_parse_json_comments(self):
        text = '{"key": "value"} // This is a comment'
        result = clean_and_parse_json(text)
        self.assertEqual(result, {"key": "value"})

        text = '{"url": "http://example.com"}'
        result = clean_and_parse_json(text)
        self.assertEqual(result, {"url": "http://example.com"})

    def test_clean_and_parse_json_url_path(self):
        text = '{"url": "http://example.com/foo//bar"}'
        result = clean_and_parse_json(text)
        self.assertEqual(result, {"url": "http://example.com/foo//bar"})

    def test_clean_and_parse_json_url_path_with_trailing_comma(self):
        text = '{"url": "http://example.com/foo//bar",}'
        result = clean_and_parse_json(text)
        self.assertEqual(result, {"url": "http://example.com/foo//bar"})

    def test_clean_and_parse_json_comment_inside_string(self):
        # This case was previously broken
        text = '{"data": "This is // not a comment", } // This is a comment'
        result = clean_and_parse_json(text)
        self.assertEqual(result, {"data": "This is // not a comment"})

if __name__ == '__main__':
    unittest.main()
