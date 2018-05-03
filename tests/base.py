import json
import unittest

from fardel.app import create_app
from fardel.ext import db
from fardel.core.auth.models import User, Group

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

    def request(self, method, url, with_token, with_rtoken, data=None, **kwargs):
        token = self.get_token(with_token, with_rtoken)
        headers = {}
        data = data or {}
        if with_token or with_rtoken:
            headers = {
                "Authorization": 'Bearer %s' % token
            }
        if method == "get":
            return self.client.get(
                url, data=json.dumps(data),
                content_type='application/json',
                headers=headers
            )
        elif method == "post":
            return self.client.post(
                url, data=json.dumps(data),
                content_type='application/json',
                headers=headers
            )
        elif method == "delete":
            return self.client.delete(
                url, data=json.dumps(data),
                content_type='application/json',
                headers=headers
            )            
        elif method == "put":
            return self.client.put(
                url, data=json.dumps(data),
                content_type='application/json',
                headers=headers
            )

    def post(self, url, data=None, with_token=True, with_rtoken=False, **kwargs):
        return self.request('post', url, with_token, with_rtoken, data=data, **kwargs)

    def get(self, url, with_token=True, with_rtoken=False, data=None, **kwargs):
        return self.request('get', url, with_token, with_rtoken, data=data, **kwargs)

    def delete(self, url, data=None, with_token=True, with_rtoken=False, **kwargs):
        return self.request('delete', url, with_token, with_rtoken, data=data, **kwargs)

    def put(self, url, data=None, with_token=True, with_rtoken=False, **kwargs):
        return self.request('put', url, with_token, with_rtoken, data=data, **kwargs)

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


class BasePanelTestCase(BaseTestCase):
    group_name = "Test"
    def create_simple_group(self):
        with self.app.app_context():
            g = Group(name=self.group_name)
            db.session.add(g)
            db.session.flush()
            g.add_permission('can_get_users')
            db.session.commit()
            return g

    def create_admin(self):
        with self.app.app_context():
            u = User(email=self.email, password=self.password)
            db.session.add(u)
            u.set_admin()

    def create_staff(self):
        with self.app.app_context():
            u = User(email=self.email, password=self.password)
            db.session.add(u)
            u.set_staff()

    def set_staff_to_group(self, g):
        with self.app.app_context():
            u = User.query.filter_by(email=self.email).first()
            u.group = g
            db.session.commit()