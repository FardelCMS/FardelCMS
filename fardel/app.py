"""
Where a RatSnake app is created.
"""

import json

import sqlalchemy

from flask import Flask, request, jsonify, redirect, url_for, render_template

from fardel import core
from fardel.ext import  db, jwt, cache
from fardel.config import DevConfig, ProdConfig

__all__ = ['create_app']

DEFAULT_APP_NAME = 'boghche'

def create_app(develop=False):
    app = Flask(DEFAULT_APP_NAME)

    configure_app(app, develop)
    configure_addons(app)
    configure_views(app)
    configure_extentions(app)
    return app

def configure_app(app, develop):
    if develop:
        app.config.from_object(DevConfig)
    else:
        app.config.from_object(ProdConfig)

def configure_addons(app):
    from fardel.core.auth.views import mod as auth
    from fardel.core.panel.views import mod as panel
    from fardel.core.media.views import mod as media
    app.register_blueprint(auth)
    app.register_blueprint(panel)
    app.register_blueprint(media)

    for app_name in app.config['ACTIVE_APPS']:

        bp = __import__('fardel.apps.%s' % app_name, fromlist=['views'])
        
        try:
            app.register_blueprint(bp.views.mod)
        except:
            print("[WARNING] : %s app doesn't have blueprint." % app_name)

def configure_views(app):
    app.add_url_rule('/api/search/', 'search', core.search)

def configure_extentions(app):
    db.init_app(app)
    with app.app_context():
        db.configure_mappers()
    jwt.init_app(app)
    cache.init_app(app)