import sys

from fardel.ext import db
from ..base import BasePanelTestCase


class BlogPanelApiTestCase(BasePanelTestCase):
	def test_publish(self):
		response = self.client.publish('/api/panel/blog/posts/')
		print(response.data)