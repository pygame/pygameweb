__version__ = '0.0.0'


def create_app(object_name='pygameweb.config.Config'):
    """returns a flask app.

    http://flask.pocoo.org/docs/patterns/appfactories/
    """

    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(object_name)

    return app
