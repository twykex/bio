import unittest
import os
import uuid
from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_path = f"test_{uuid.uuid4()}.db"
        self.db = Database(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_create_user(self):
        user_id = self.db.create_user("test@example.com", "hash", "Test User")
        self.assertIsNotNone(user_id)

        user = self.db.get_user_by_email("test@example.com")
        self.assertEqual(user['name'], "Test User")
        self.assertFalse(user['is_guest'])

    def test_create_guest(self):
        guest_id = self.db.create_user(None, None, "Guest", is_guest=True)
        self.assertIsNotNone(guest_id)

        user = self.db.get_user_by_id(guest_id)
        self.assertTrue(user['is_guest'])
        self.assertEqual(user['name'], "Guest")

    def test_convert_guest(self):
        guest_id = self.db.create_user(None, None, "Guest", is_guest=True)

        success, msg = self.db.convert_guest_to_user(guest_id, "new@example.com", "newhash", "Real User")
        self.assertTrue(success)

        user = self.db.get_user_by_id(guest_id)
        self.assertFalse(user['is_guest'])
        self.assertEqual(user['email'], "new@example.com")
        self.assertEqual(user['name'], "Real User")

    def test_save_load_data(self):
        user_id = self.db.create_user("data@example.com", "hash", "Data User")
        data = {"key": "value", "list": [1, 2, 3]}

        self.db.save_user_data(user_id, data)
        loaded = self.db.load_user_data(user_id)

        self.assertEqual(loaded, data)

if __name__ == '__main__':
    unittest.main()
