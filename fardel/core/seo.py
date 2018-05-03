from fardel.ext import db


class SeoModel(object):
	seo_title = db.Column(db.String(70))
	seo_description = db.Column(db.String(300))

	def seo_dict(self):
		return {
			'seo_title': self.seo_title,
			'seo_description': self.seo_description
		}