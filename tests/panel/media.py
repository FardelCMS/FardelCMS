import sys

from web.ext import db
from web.core.auth.models import User
from ..base import BasePanelTestCase

if sys.version_info <= (2, 7):
    from StringIO import StringIO
    ClassIO = StringIO
else:
    from io import BytesIO


class MediaApiTestCase(BasePanelTestCase):
    files = []
    def test(self):
        self.create_admin()
        self.login()
        file = open('boghche.jpg', 'rb')
        headers = {
            "Authorization": 'Bearer %s' % self.access_token
        }
        
        response = self.client.post('/api/panel/files/', buffered=True,
                               content_type='multipart/form-data',
                               data={'path' : 'images',
                                     'file' : (BytesIO(file.read()), 'boghche.jpg')},
                               headers=headers
        )
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'File saved successfully')
        self.assertEqual(response.status_code, 200)
        self.files.append(json_data['file']['url'])
        file.close()
        
        file = open('boghche.jpg', 'rb')
        response = self.client.post('/api/panel/files/', buffered=True,
                               content_type='multipart/form-data',
                               data={'file' : (BytesIO(file.read()), 'boghche.jpg')},
                               headers=headers
        )
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'File saved successfully')
        self.assertEqual(response.status_code, 200)
        self.files.append(json_data['file']['url'])
        file.close()

        response = self.delete('/api/panel/files/', data={'url':self.files.pop()})
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'File deleted successfully')
        self.assertEqual(response.status_code, 200)

        response = self.delete('/api/panel/files/', data={'url':self.files.pop()})
        json_data = self.get_json(response.data)
        self.assertEqual(json_data['message'], 'File deleted successfully')
        self.assertEqual(response.status_code, 200)

    def clean(self):
        with self.app.app_context():
            u = User.query.filter_by(email=self.email).delete()
            db.session.commit()

    def tearDown(self):
        self.clean()
        self.access_token = None