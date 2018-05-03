"""
Required flask extensions objects in RatSnake are created here.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cache import Cache

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()