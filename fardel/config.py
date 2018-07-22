import os 

from pathlib import Path
from flask_babel import lazy_gettext


PATH_TO_ROOT = Path(__file__).parent.parent

class BaseConfig(object):
    VERSION = "0.1.0"
    MINIFY = False

    SECRET_KEY = 'qt584635@(*$(KC=oijr )*@$*^SAd- okasfoijh*(@Y$*)A)S(+D' # move this to os.environment

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_REFRESH_TOKEN_EXPIRES = False
    JWT_ACCESS_TOKEN_EXPIRES = False

    UPLOAD_FOLDER = Path(__file__).parent.parent / 'uploads'

    MERCHANT_ID = '5eaa6812-a1fb-11e7-b0e3-000c295eb8fc'  # Required
    ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'  # Required

    ACTIVE_APPS = (
        # "blog",
        "auth_address",
        "ecommerce",
    )

    SITE_NAME = lazy_gettext("Fardel")

    CACHE_TYPE = 'simple'

    BABEL_DEFAULT_LOCALE = "fa"
    BABEL_TRANSLATION_DIRECTORIES = str(PATH_TO_ROOT / "translations")

    # MAIL_SERVER = ""
    # MAIL_USERNAME = ""
    # MAIL_PASSWORD = ""

    # ADMIN_EMAIL = ""

    # MAIL_SUBJECT_PREFIX = '[]'
    # MAIL_SENDER = 'Info <@.com>'


    # ZARINPAL_MERCHANT_ID = ''
    # ZARINPAL_WEBSERVICE = ''

    # RECAPTCHA_ENABLED = True
    # RECAPTCHA_SITE_KEY = ""
    # RECAPTCHA_SECRET_KEY = ""
    # RECAPTCHA_THEME = "light"
    # RECAPTCHA_TYPE = "image"
    # RECAPTCHA_SIZE = "compact"
    # RECAPTCHA_RTABINDEX = 10


class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'postgresql://dev_shop:123@localhost/dev_shop'
    DEBUG = True


class ProdConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'postgresql://dev_shop:123@localhost/dev_shop'
    DEBUG = False