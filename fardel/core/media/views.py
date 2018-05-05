"""
All files are accessible through this url

:URL: ``/uploads/<path_to_file>``

"""


from flask import send_file, current_app

from . import mod
from .models import setup_permissions


@mod.before_app_first_request
def create_permissions():
    setup_permissions()


@mod.route('/uploads/<path:path_to_file>')
def file_loader(path_to_file):
	""" Use this function only in development mode """
	return send_file(str(current_app.config['UPLOAD_FOLDER'] / path_to_file))