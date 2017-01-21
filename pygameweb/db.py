""" Database code using sqlalchemy.
"""


def init(app, engine, session_factory):
    """Adds app.engine, and app.session_factory. Creates them if not passed in.

    :param app: flask app.
    :param engine: sqlalchemy engine.
    :param session_factory: session factory.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # http://flask-sqlalchemy-session.readthedocs.io/en/v1.1/
    from flask_sqlalchemy_session import flask_scoped_session

    app.engine = (create_engine(app.config["SQLALCHEMY_DATABASE_URI"]) if engine is None
                  else engine)
    app.session_factory = (sessionmaker(bind=app.engine) if session_factory is None
                           else session_factory)
    app.scoped_session = flask_scoped_session(app.session_factory, app)
