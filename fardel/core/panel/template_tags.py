from flask import current_app
from .sidebar import panel_sidebar


def get_sidebar():
	return panel_sidebar.render()

def get_sitename():
	return current_app.config['SITE_NAME']


def add_globals(app):
	app.jinja_env.globals['get_sitename'] = get_sitename
	app.jinja_env.globals['get_sidebar'] = get_sidebar