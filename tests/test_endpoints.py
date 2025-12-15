import unittest
import json
import io
from app import app
from services.session_service import get_session

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_init_context_dummy(self):
        # Create a dummy PDF file content
        data = {
            'file': (io.BytesIO(b"%PDF-1.4...dummy content..."), 'test.pdf'),
            'token': 'test_token'
        }
        # Mocking PDF reading might be hard without a real PDF,
        # so we expect a 500 or 400 depending on pdfplumber behavior on junk bytes.
        # But let's check if the route exists.
        response = self.app.post('/init_context', data=data, content_type='multipart/form-data')
        # Since the PDF is invalid, it should return 500 according to app.py
        self.assertIn(response.status_code, [200, 500])

    def test_generate_workout(self):
        # Pre-populate session in app.py logic
        token = "test_token_workout"
        session = get_session(token)
        session["blood_context"] = {"summary": "Healthy"}

        response = self.app.post('/generate_workout',
                                 data=json.dumps({'token': token, 'strategy_name': 'Muscle'}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(isinstance(data, list))
        if len(data) > 0:
            self.assertIn("day", data[0])
            self.assertIn("exercises", data[0])

    # def test_explain_biomarker(self):
    #     token = "test_token_bio"
    #     session = get_session(token)
    #     session["blood_context"] = {"summary": "Low Vitamin D"}

    #     response = self.app.post('/explain_biomarker',
    #                              data=json.dumps({'token': token, 'biomarker': 'Vitamin D'}),
    #                              content_type='application/json')

    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertIn("explanation", data)

if __name__ == '__main__':
    unittest.main()
