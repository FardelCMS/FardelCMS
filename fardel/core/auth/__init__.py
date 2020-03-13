import pathlib

from flask import Blueprint

auth_package_path = pathlib.Path(__file__).parent

mod = Blueprint(
    'auth',
    'auth',
    static_folder=str(auth_package_path / 'static'),
    template_folder=str(auth_package_path / 'templates'),
    url_prefix="/api/auth",
)
