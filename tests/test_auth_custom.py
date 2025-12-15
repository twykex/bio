import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from services.user_store import users

class TestAuthCustom(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        users.clear()

    def test_signup_no_password(self):
        # Missing password field entirely
        response = self.app.post('/signup', data={
            'name': 'Test User',
            'email': 'test@example.com'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200) # 200 because of follow_redirects=True (login page)
        self.assertIn(b'Password is required', response.data)
        self.assertNotIn('test@example.com', users)

    def test_signup_empty_password(self):
        # Empty password string
        response = self.app.post('/signup', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': ''
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password is required', response.data)
        self.assertNotIn('test@example.com', users)

if __name__ == '__main__':
    unittest.main()
