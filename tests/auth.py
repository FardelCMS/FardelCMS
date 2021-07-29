from fardel.ext import db
from fardel.core.auth.models import User

from .base import BaseTestCase


class AuthTestCase(BaseTestCase):
    def logout(self):
        self.access_token = None
        return self.post('/api/auth/logout/')

    def logout_refresh(self):
        self.refresh_token = None
        return self.post('/api/auth/logout-refresh/')

    def test_register(self):
        json_data, code = self.register()
        self.assertEqual(json_data['message'], 'Successfully registered')
        self.assertIsNotNone(json_data['access_token'])
        self.assertIsNotNone(json_data['refresh_token'])
        self.assertEqual(200, code)

        json_data, code = self.register()
        self.assertEqual(json_data['message'],
                         'A user with this email already exists.')
        self.assertEqual(409, code)

        response = self.post('/api/auth/register/',
                             data={'password': self.password}, with_token=False)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Invalid form submitted')
        self.assertEqual(400, response.status_code)

        response = self.post('/api/auth/register/',
                             data={'email': self.email}, with_token=False)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Invalid form submitted')
        self.assertEqual(400, response.status_code)

    def test_login_logout_refresh(self):
        self.register()
        json_data, code = self.login()
        self.assertEqual(json_data['message'], 'Successfully logined')
        self.assertEqual(200, code)

        response = self.post(
            '/api/auth/login/', data={'password': self.password}, with_token=False)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Invalid form submitted')
        self.assertEqual(400, response.status_code)

        response = self.post('/api/auth/login/',
                             data={'email': self.email}, with_token=False)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Invalid form submitted')
        self.assertEqual(400, response.status_code)

        response = self.post('/api/auth/logout/')
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Access token has been revoked')
        self.assertEqual(200, response.status_code)

        response = self.post('/api/auth/logout-refresh/', with_rtoken=True)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'],
                         'Refresh token has been revoked')
        self.assertEqual(200, response.status_code)

        response, json_data = self.profile()
        self.assertEqual(json_data['message'], "Token has been revoked")
        self.assertEqual(401, response.status_code)

    def test_profile(self):
        json_data, _ = self.register()
        self.assertEqual(json_data.get('message'), "Successfully registered")

        response, json_data = self.profile()
        self.assertIsNotNone(json_data['user'])
        self.assertEqual(200, response.status_code)

        response = self.put('/api/auth/profile/', data={'first_name': 'test2'})
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['user']['first_name'], 'test2')
        self.assertEqual(200, response.status_code)

    def test_refresh_token(self):
        json_data, response = self.register()
        self.assertEqual(json_data.get('message'), "Successfully registered")

        response = self.post('/api/auth/refresh-token/', with_rtoken=True)
        json_data = self.get_json(response.data)
        self.assertIsNotNone(json_data['access_token'])
        self.assertEqual(200, response.status_code)

    def clean(self):
        with self.app.app_context():
            u = User.query.filter_by(email=self.email).delete()
            db.session.commit()

    def setUp(self):
        super().setUp()
        self.clean()
        self.access_token = None
