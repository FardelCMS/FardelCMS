from web.ext import db

from web.core.auth.models import User, Group

from .base import BaseTestCase

class PanelAuthTestCase(BaseTestCase):
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