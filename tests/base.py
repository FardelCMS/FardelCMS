import json
import unittest

from web.app import create_app

class BaseTestCase(unittest.TestCase):
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
        
    def profile(self):
        response = self.get('/api/auth/profile/')
        json_data = self.get_json(response.data)
        return response, json_data
