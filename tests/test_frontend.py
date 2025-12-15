import unittest
from app import app

class TestFrontend(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_renders(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BioFlow', response.data)
        # Check if new landing content is present
        self.assertIn(b'Your Body', response.data)
        self.assertIn(b'Decoded', response.data)
