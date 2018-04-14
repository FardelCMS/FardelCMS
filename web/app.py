"""
Where a RatSnake app is created.
"""

import json

import sqlalchemy
from flask import Flask, request, jsonify, redirect, url_for, render_template

from .ext import  db, jwt
from .config import DevConfig, ProdConfig

__all__ = ['create_app']

DEFAULT_APP_NAME = 'gomnama'


def create_app(develop=False):
    app = Flask(DEFAULT_APP_NAME)

    configure_app(app, develop)
    configure_addons(app)
    configure_extentions(app)
    return app

def configure_app(app, develop):
    if develop:
        app.config.from_object(DevConfig)
    else:
        app.config.from_object(ProdConfig)


def configure_addons(app):
    from web.core.auth.views import mod as auth
    from web.core.panel.views import mod as panel
    app.register_blueprint(auth)
    app.register_blueprint(panel)

def configure_errorhandlers(app):
    pass

def configure_extentions(app):
    db.init_app(app)
    jwt.init_app(app)