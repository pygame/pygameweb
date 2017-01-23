"""Flask app config.

See http://flask.pocoo.org/docs/0.12/config/

Uses environment variables to make things easier for deployment and local development.

See pygameweb.__init__ where we automatically look at these variables.
"""

import os

def truthy_config(key):
    """Returns True if an environment var contains a truth variable.

    Things like True, true, and 1 are true.
    """
    val = os.environ.get(key)
    if val is None:
        return False
    if val.lower() in ['true', '1']:
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
