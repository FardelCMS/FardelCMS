import json

from web.app import create_app
from web.ext import db
from web.core.auth.models import User

from unittest import TestCase


class BaseTestCase(TestCase):
    access_token = None
    refresh_token = None
    email = 'test@test.com'
    password = 'test123'

    def setUp(self):
        self.app = create_app(develop=True)
        self.client = self.app.test_client()

    def get_token(self, with_token, with_rtoken):
        if with_rtoken:
            token = self.refresh_token
        else:
            token = self.access_token
        return token

    def post(self, url, data=None, with_token=True, with_rtoken=False):
        token = self.get_token(with_token, with_rtoken)
        if with_token or with_rtoken:
            headers = {
                "Authorization": 'Bearer %s' % token
            }
            return self.client.post(
                url, data=json.dumps(data),
                content_type='application/json',
                headers=headers
            )
        return self.client.post(url, data=json.dumps(data),content_type='application/json')

    def get(self, url, data=None, with_token=True, with_rtoken=False):
        token = self.get_token(with_token, with_rtoken)
        if with_token:
            headers = {
                "Authorization": 'Bearer %s' % token
            }
            return self.client.get(url, headers=headers)
        return self.client.get(url)


    def get_json(self, data):
        return json.loads(data)


class AuthTestCase(BaseTestCase):
    def register(self):
        response = self.post(
            '/api/auth/register/',
            data={'email':self.email, 'password':self.password},
            with_token=False
        )
        json_data = self.get_json(response.data)
        if json_data.get('message') == "Successfully registered":
            self.access_token = json_data.get('access_token')
            self.refresh_token = json_data.get('refresh_token')
            self.assertIsNotNone(self.access_token)
            self.assertIsNotNone(self.refresh_token)
        return json_data, response.status_code

    def login(self):
        response = self.post(
            '/api/auth/login/',
            data={'email':self.email, 'password':self.password},
        )
        json_data = self.get_json(response.data)
        if json_data.get('message') == "Successfully logined":
            self.access_token = json_data.get('access_token')
            self.refresh_token = json_data.get('refresh_token')
            self.assertIsNotNone(self.access_token)
            self.assertIsNotNone(self.refresh_token)
        return json_data, response.status_code

    def profile(self):
        response = self.get('/api/auth/profile/')
        json_data = self.get_json(response.data)
        return response, json_data

    def logout(self):
        self.access_token = None
        return self.post('/api/auth/logout/')

    def logout_refresh(self):
        self.refresh_token = None
        return self.post('/api/auth/logout-refresh/')

    def test_register(self):
        json_data, code = self.register()
        self.assertEqual(json_data['message'], 'Successfully registered')
        self.assertEqual(200, code)

        json_data, code = self.register()
        self.assertEqual(json_data['message'], 'A user with this email already exists.')
        self.assertEqual(409, code)

        response = self.post('/api/auth/register/', data={'password':self.password}, with_token=False)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Unvalid form submitted')
        self.assertEqual(400, response.status_code)

        response = self.post('/api/auth/register/', data={'email':self.email}, with_token=False)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Unvalid form submitted')
        self.assertEqual(400, response.status_code)

    def test_login_logout_refresh(self):
        self.register()
        json_data, code = self.login()
        self.assertEqual(json_data['message'], 'Successfully logined')
        self.assertEqual(200, code)

        response = self.post('/api/auth/login/', data={'password':self.password}, with_token=False)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Unvalid form submitted')
        self.assertEqual(400, response.status_code)

        response = self.post('/api/auth/login/', data={'email':self.email}, with_token=False)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Unvalid form submitted')
        self.assertEqual(400, response.status_code)

        response = self.post('/api/auth/logout/')
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Access token has been revoked')
        self.assertEqual(200, response.status_code)

        response = self.post('/api/auth/logout-refresh/', with_rtoken=True)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'Refresh token has been revoked')
        self.assertEqual(200, response.status_code)

        response, json_data = self.profile()
        self.assertEqual(json_data['message'], "Token has been revoked")
        self.assertEqual(401, response.status_code)

    def test_profile(self):
        self.register()
        response, json_data = self.profile()
        self.assertIsNotNone(json_data['user'])
        self.assertEqual(200, response.status_code)

    def test_refresh_token(self):
        self.register()
        response = self.post('/api/auth/refresh-token/', with_rtoken=True)
        json_data = self.get_json(response.data)
        self.assertIsNotNone(json_data['access_token'])
        self.assertEqual(200, response.status_code)

    def clean(self):
        with self.app.app_context():
            u = User.query.filter_by(email=self.email).delete()
            db.session.commit()

    def tearDown(self):
        self.clean()
        self.access_token = None