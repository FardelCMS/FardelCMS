
class BaseConfig(object):
    VERSION = "0.1.0"
    MINIFY = False

    SECRET_KEY = 'qt584635@(*$(KC=oijr )*@$*^SAd- okasfoijh*(@Y$*)A)S(+D'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

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
    SQLALCHEMY_DATABASE_URI = 'postgresql://arash_shop:123@localhost/arash_shop'
    DEBUG = True


class ProdConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = ''
    DEBUG = False