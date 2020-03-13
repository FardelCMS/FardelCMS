import os

from pathlib import Path
from flask_babel import lazy_gettext


PATH_TO_ROOT = Path(__file__).parent.parent


class BaseConfig(object):
    VERSION = "0.1.0"
    MINIFY = False

    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@server_address/db_name'
    DEBUG = True

    SECRET_KEY = 'GET SECRET KEY FROM ENV'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_REFRESH_TOKEN_EXPIRES = False
    JWT_ACCESS_TOKEN_EXPIRES = False

    UPLOAD_FOLDER = Path(__file__).parent.parent / 'uploads'

    FARDEL_APP_PATH = "fardel_apps"
    ACTIVE_APPS = (
        "blog",
        "auth_address",
        "ecommerce",
    )

    SITE_NAME = lazy_gettext("Fardel")

    CACHE_TYPE = 'simple'

    PANEL_BASE_DIR = "ltr"
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_TRANSLATION_DIRECTORIES = str(PATH_TO_ROOT / "translations")

    SENTRY_DSN = ""

    EMAIL_VERIFICATION_EMAIL_SENDER = os.getenv("EMAIL_VERIFICATION_EMAIL_SENDER")
    EMAIL_VERIFICATION_ACTIVE = bool(os.getenv("EMAIL_VERIFICATION_ACTIVE", default=False))

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", default=465))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
