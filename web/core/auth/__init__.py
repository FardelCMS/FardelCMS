from .models import User

from flask import Blueprint

mod = Blueprint('auth', __name__, url_prefix="/api/auth")