"""
Required flask extensions objects in RatSnake are created here.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cache import Cache
from flask_login import LoginManager
from flask_babel import Babel


db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
login_manager = LoginManager()
babel = Babel()