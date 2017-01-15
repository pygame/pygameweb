"""Flask app config.

See http://flask.pocoo.org/docs/0.12/config/
"""

import os

class Config(object):
    """App config.
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('APP_DATABASE_URL')
    PORT = int(os.getenv('APP_PORT', '6000'))
    HOST = os.getenv('APP_HOST', 'localhost')
