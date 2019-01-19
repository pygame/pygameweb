"""Flask app config.

See http://flask.pocoo.org/docs/0.12/config/

Uses environment variables to make things easier for
deployment and local development.

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
    CONFIG_PREFIX = 'APP_'
    SQLALCHEMY_DATABASE_URI = os.environ.get(CONFIG_PREFIX + 'DATABASE_URL')
    PORT = int(os.getenv(CONFIG_PREFIX + 'PORT', '5000'))
    HOST = os.getenv(CONFIG_PREFIX + 'HOST', 'localhost')
    DEBUG = truthy_config(CONFIG_PREFIX + 'DEBUG')
    SECRET_KEY = os.getenv(CONFIG_PREFIX + 'SECRET_KEY')
    WWW = os.getenv(CONFIG_PREFIX + 'WWW')
    TESTING = False
    ADMIN = os.getenv(CONFIG_PREFIX + 'ADMIN', False)

    # http://flask-security-fork.readthedocs.io/en/latest/configuration.html
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = os.getenv(CONFIG_PREFIX + 'SECRET_KEY')
    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_EMAIL_SENDER = os.getenv(CONFIG_PREFIX + 'SECURITY_EMAIL_SENDER', '')
    SECURITY_DEFAULT_REMEMBER_ME = os.getenv(CONFIG_PREFIX + 'SECURITY_DEFAULT_REMEMBER_ME', True)

    MAIL_SERVER = os.getenv(CONFIG_PREFIX + 'MAIL_SERVER', '')
    MAIL_PORT = int(os.getenv(CONFIG_PREFIX + 'MAIL_PORT', 465))
    MAIL_USE_SSL = truthy_config(CONFIG_PREFIX + 'MAIL_USE_SSL', True)

    MAIL_USERNAME = os.getenv(CONFIG_PREFIX + 'MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv(CONFIG_PREFIX + 'MAIL_PASSWORD', '')
    MAIL_SUPPRESS_SEND = truthy_config(CONFIG_PREFIX + 'DEBUG')
    MAIL_DEBUG = truthy_config(CONFIG_PREFIX + 'DEBUG')

    # CACHE_TYPE = 'simple'
    CACHE_TYPE = 'null' if truthy_config(CONFIG_PREFIX + 'DEBUG') else 'simple'
    """ flask_caching is off in debug mode.
    """

    # Disable the flask-caching warning message.
    # https://pythonhosted.org/Flask-Caching/#configuring-flask-caching
    if CACHE_TYPE == 'null':
        CACHE_NO_NULL_WARNING = True

    RATELIMIT_GLOBAL = ('5000 per day, 5000 per hour'
                        if truthy_config(CONFIG_PREFIX + 'DEBUG')
                        else '200 per day, 50 per hour')

    STACK_KEY = os.getenv(CONFIG_PREFIX + 'STACK_KEY', '')

    COMMENT_MODEL = os.getenv(CONFIG_PREFIX + 'COMMENT_MODEL', 'comment_spam_model.pkl')
    """For the comment spam classifier model file.
    """

    GITHUB_RELEASES_OAUTH = os.getenv(CONFIG_PREFIX + 'GITHUB_RELEASES_OAUTH', None)
    """ For syncing github releases to pygame_org.
    """

