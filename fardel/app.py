"""
Where a RatSnake app is created.
"""

import logging
import json

import sqlalchemy
from raven.contrib.flask import Sentry

from flask import Flask, request, jsonify, redirect, url_for, render_template

from fardel import core
from fardel.ext import db, jwt, cache, login_manager, babel, mail


__all__ = (
    'Fardel',
)

DEFAULT_APP_NAME = 'fardel'


class Fardel(object):
    ignored_panel_urls = ['static']

    def __init__(self, config_class, **flask_options):
        self.app = Flask(DEFAULT_APP_NAME, **flask_options)
        self.panels = []

        self.configure_app(config_class)
        self.configure_addons()
        self.configure_views()
        self.configure_extentions()
        self.configure_logger()
        self.init_jinja_globals()
        self.configure_sentry()

    def configure_app(self, config_class):
        self.app.config.from_object(config_class)

    def configure_addons(self):
        from fardel.core.auth.views import mod as auth
        from fardel.core.panel.views import mod as panel
        from fardel.core.media.views import mod as media
        self.app.register_blueprint(auth)
        self.app.register_blueprint(panel)
        self.app.register_blueprint(media)

        fardel_apps_path = self.app.config['FARDEL_APP_PATH']

        for app_name in self.app.config['ACTIVE_APPS']:
            if app_name.startswith("fardel_"):
                try:
                    bp = __import__(app_name, fromlist=["views", "panel"])

                    if hasattr(bp, "panel"):
                        self._register_panel(self.app, bp.panel.mod, app_name)
                    else:
                        self.app.logger.debug("No admin panel for %s" % app_name)

                    try:
                        self.app.register_blueprint(bp.views.mod)
                        self.app.logger.debug("Module %s regiestered" % app_name)
                    except:
                        self.app.logger.warning("%s app doesn't have blueprint." % app_name)
                        self.app.logger.warning(err, exc_info=True)
                except Exception as err:
                    self.app.logger.warning("%s app not found" % app_name)
                    self.app.logger.warning(err, exc_info=True)
            else:
                try:
                    bp = __import__('{fardel_apps_path}.{app_name}'.format(
                        app_name=app_name,
                        fardel_apps_path=fardel_apps_path
                    ), fromlist=['views', 'panel'])

                    if hasattr(bp, 'panel'):
                        self._register_panel(self.app, bp.panel.mod, app_name)
                    else:
                        self.app.logger.debug("No admin panel for %s" % app_name)

                    try:
                        self.app.register_blueprint(bp.views.mod)
                        self.app.logger.debug("Module %s registered" % app_name)
                    except Exception as err:
                        self.app.logger.warning("%s app doesn't have blueprint." % app_name)
                        self.app.logger.warning(err, exc_info=True)

                except Exception as err:
                    self.app.logger.warning("%s app not found" % app_name)
                    self.app.logger.warning(err, exc_info=True)

    def configure_views(self):
        self.app.add_url_rule('/api/search/', 'search', core.search)

    def configure_logger(self):
        self.app.logger = logging.getLogger("fardel")

    def configure_extentions(self):
        db.init_app(self.app)
        with self.app.app_context():
            db.configure_mappers()
        jwt.init_app(self.app)
        cache.init_app(self.app)
        login_manager.init_app(self.app)
        babel.init_app(self.app)
        mail.init_app(self.app)

    def configure_sentry(self):
        if self.app.config['SENTRY_DSN']:
            sentry = Sentry(self.app, dsn=self.app.config['SENTRY_DSN'])

    def init_jinja_globals(self):
        from fardel.core.panel.template_tags import add_globals
        add_globals(self.app)

    def _register_panel(self, app, blueprint, app_name):
        if blueprint.name.endswith("panel"):
            self.panels.append(blueprint.name)
            self.app.register_blueprint(blueprint)
            for rule in self.app.url_map.iter_rules():
                endpoint = rule.endpoint.split('.')
                if endpoint[0] in self.panels and not rule.rule.startswith("/panel/"):
                    raise Exception("Panel url must start with /panel/")
                if endpoint[0] in self.panels and endpoint[1] not in self.ignored_panel_urls:
                    view_func = self.app.view_functions.get(rule.endpoint)
                    has_staff_required = False
                    has_admin_required = False
                    if hasattr(view_func, 'decorators'):
                        has_staff_required = view_func.decorators.get('staff_required', False)
                        has_admin_required = view_func.decorators.get('admin_required', False)

                    if not has_staff_required and not has_admin_required:
                        raise Exception("No staff_required or admin_required for panel function %s" % rule.endpoint)

            self.app.logger.debug("Admin panel for %s registered" % app_name)
        else:
            raise Exception("Panel blueprint's name must ends with panel")
