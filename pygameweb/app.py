

def create_app(object_name='pygameweb.config.Config',
               engine=None,
               session_factory=None):
    """returns a flask app.

    http://flask.pocoo.org/docs/patterns/appfactories/

    :param engine: an sqlalchemy engine.
    :param session_factory: an sqlalchemy session_factory.
    """

    from flask import Flask
    from flask_bootstrap import Bootstrap
    from pygameweb import db
    app = Flask(__name__)
    app.config.from_object(object_name)
    Bootstrap(app)

    db.init(app, engine, session_factory)

    return app


def add_views_front(app):
    """ Adds all the front end views to the app.

    Kept separate from create_app so we can test individual views.
    """
    from pygameweb.wiki.views import add_wiki_blueprint
    add_wiki_blueprint(app)
