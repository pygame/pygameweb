"""Flask app config.

See http://flask.pocoo.org/docs/0.12/config/

Uses environment variables to make things easier for deployment and local development.

See pygameweb.__init__ where we automatically look at these variables.
"""

import os

def truthy_config(key, default=False):
    """Returns True if an environment var contains a truth variable.

    Things like True, true, and 1 are true.
    """
    val = os.environ.get(key, default)
    if val is None or val is False:
        return False
    if val is True or val.lower() in ['true', '1']:
        return True
    return False


class Config(object):
    """App config.
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('APP_DATABASE_URL')
    PORT = int(os.getenv('APP_PORT', '5000'))
    HOST = os.getenv('APP_HOST', 'localhost')
    DEBUG = truthy_config('APP_DEBUG')
    SECRET_KEY = os.getenv('APP_SECRET_KEY')
    WWW = os.getenv('APP_WWW')

    # http://flask-security-fork.readthedocs.io/en/latest/configuration.html
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = os.getenv('APP_SECRET_KEY')
    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_EMAIL_SENDER = os.getenv('APP_SECURITY_EMAIL_SENDER', '')

    MAIL_SERVER = os.getenv('APP_MAIL_SERVER', '')
    MAIL_PORT = int(os.getenv('APP_MAIL_PORT', 465))
    MAIL_USE_SSL = truthy_config('APP_MAIL_USE_SSL', True)

    MAIL_USERNAME = os.getenv('APP_MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('APP_MAIL_PASSWORD', '')
    MAIL_SUPPRESS_SEND = truthy_config('APP_DEBUG')

    TESTING = False
    MAIL_DEBUG = truthy_config('APP_DEBUG')

    CACHE_TYPE = 'null' if truthy_config('APP_DEBUG') else 'simple'
    """ flask_caching is off in debug mode.
    """
