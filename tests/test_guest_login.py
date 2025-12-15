import unittest
from app import app
from flask import session

class GuestLoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_guest_login_route(self):
        # First check if route exists and redirects
        response = self.app.get('/guest-login')
        # Expect 302 Redirect
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/dashboard') or '/dashboard' in response.location)

    def test_guest_login_session(self):
        with self.app as c:
            response = c.get('/guest-login', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('user_id', session)
            self.assertTrue(session['user_id'].startswith('guest_'))
            self.assertIn(b'BioFlow AI', response.data)

if __name__ == '__main__':
    unittest.main()
