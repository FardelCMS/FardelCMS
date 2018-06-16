__version__ = "1.0.0"

from flask import Blueprint

mod = Blueprint('auth_address', __name__, url_prefix="/api/auth")