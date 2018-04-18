from web.ext import db

from web.core.auth.models import User, Group

from .base import BaseTestCase

__all__ = (
    'PanelAuthTestCase',
    'UserApiTestCase',
)

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


class PanelAuthTestCase(BasePanelTestCase):
    def test_not_admin_permission(self):
        self.register()
        response = self.get('/api/panel/users/')
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.")
        self.assertEqual(response.status_code, 403)

    def test_admin_permission(self):
        self.create_admin()
        self.login()
        response = self.get('/api/panel/users/')
        json_data = self.get_json(response.data)
        self.assertIsInstance(json_data['users'], list)

    def test_staff_permissions(self):
        self.create_staff()
        self.login()

        response = self.get('/api/panel/users/')
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.")
        self.assertEqual(response.status_code, 403)

        g = self.create_simple_group()
        self.set_staff_to_group(g)
        response = self.get('/api/panel/users/')
        json_data = self.get_json(response.data)
        self.assertIsInstance(json_data['users'], list)

    def clean(self):
        with self.app.app_context():
            u = User.query.filter_by(email=self.email).delete()
            db.session.commit()

    def tearDown(self):
        self.clean()
        self.access_token = None


class UserApiTestCase(BasePanelTestCase):
    user_sample_email = "sample@sample.com"
    user_sample_passwd = "123"
    user_sample_id = None
    first_name = 'testy'

    def test_api(self):
        self.create_admin()
        self.login()
        response, json_data = self.profile()
        admin_user_id = json_data['user']['id']

        response = self.get('/api/panel/users/')
        json_data = self.get_json(response.data)
        self.assertIsInstance(json_data['users'], list)
        self.assertEqual(response.status_code, 200)

        response = self.post('/api/panel/users/', data={
            'email':self.user_sample_email, 'password':self.user_sample_passwd
        })
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], "User successfully added")
        self.assertEqual(response.status_code, 200)
        user_id = json_data['user']['id']

        response = self.post('/api/panel/users/', data={
            'email':self.user_sample_email, 'password':self.user_sample_passwd
        })
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], "User already exists")
        self.assertEqual(response.status_code, 422)

        response = self.put('/api/panel/users/%d/' % user_id, data={
            'first_name':self.first_name})
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'User successfully updated')
        self.assertEqual(response.status_code, 200)

        response = self.delete('/api/panel/users/%d/' % user_id)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'User successfully deleted')
        self.assertEqual(response.status_code, 200)

        response = self.delete('/api/panel/users/%d/' % admin_user_id)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], "You can't delete yourself")
        self.assertEqual(response.status_code, 422)

        response = self.delete('/api/panel/users/%d/' % user_id)
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], "No user deleted")
        self.assertEqual(response.status_code, 404)


class GroupApiTestCase(BasePanelTestCase):
    pass