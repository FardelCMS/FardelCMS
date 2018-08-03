from flask import current_app
from .sidebar import panel_sidebar

def get_text_direction():
	return current_app.config['PANEL_BASE_DIR']

def rightrtl_leftltr():
	return "right" if current_app.config['PANEL_BASE_DIR'] == "rtl" else "left"

def leftrtl_rightltr():
	return "left" if current_app.config['PANEL_BASE_DIR'] == "rtl" else "right"

def get_sidebar():
	return panel_sidebar.render()

def get_sitename():
	return current_app.config['SITE_NAME']

def add_globals(app):
	app.jinja_env.globals['get_sitename'] = get_sitename
	app.jinja_env.globals['get_sidebar'] = get_sidebar
	
	app.jinja_env.globals['get_text_direction'] = get_text_direction
	app.jinja_env.globals['rightrtl_leftltr'] = rightrtl_leftltr
	app.jinja_env.globals['leftrtl_rightltr'] = leftrtl_rightltr