import unittest
from app import app

class TestOnboarding(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_onboarding_modal_present(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Check for onboarding modal ID or unique text
        self.assertIn('Analysis Complete', content)
        self.assertIn('See What\'s Possible', content)
        self.assertIn('Your Health Command Center', content)
        self.assertIn('x-show="showOnboarding"', content)
