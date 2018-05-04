import pathlib

from .decorator import *

from flask import Blueprint

panel_package_path = pathlib.Path(__file__).parent

mod = Blueprint(
	'panel',
	'panel',
	static_folder=str(panel_package_path / 'static'),
	template_folder=str(panel_package_path / 'templates'),
	url_prefix='/panel'
)