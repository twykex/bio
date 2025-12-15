import unittest
from services.json_cleaner import fix_truncated_json

class TestJsonCleaner(unittest.TestCase):
    def test_simple_fix(self):
        self.assertEqual(fix_truncated_json('{"key": "val'), '{"key": "val"}')

    def test_orphaned_key_in_object(self):
        # Should append : null and close
        self.assertEqual(fix_truncated_json('{"key": "val", "unfinished'), '{"key": "val", "unfinished": null}')

    def test_orphaned_key_colon_in_object(self):
        self.assertEqual(fix_truncated_json('{"key": "val", "unfinished":'), '{"key": "val", "unfinished": null}')

    def test_array_fix(self):
        self.assertEqual(fix_truncated_json('{"arr": ["a", "b'), '{"arr": ["a", "b"]}')

    def test_complex_nesting(self):
        input_str = '{"a": {"b": ["c", "d'
        expected = '{"a": {"b": ["c", "d"]}}'
        self.assertEqual(fix_truncated_json(input_str), expected)

    def test_string_quote_balance(self):
        self.assertEqual(fix_truncated_json('{"key": "va\\"l'), '{"key": "va\\"l"}')

if __name__ == '__main__':
    unittest.main()
