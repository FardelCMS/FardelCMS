from flask import send_file, current_app

from . import mod
from .models import *


@mod.route('/uploads/<path_to_file>')
def file_loader(path_to_file):
	""" Use this function only in development mode """
	return send_file(str(current_app.config['UPLOAD_FOLDER'] / path_to_file))