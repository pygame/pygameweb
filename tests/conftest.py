""" Fixtures for testing.

http://stackoverflow.com/questions/34466027/in-py-test-what-is-the-use-of-conftest-py-files

To make testing databases easier we need a few fixtures for
rolling back changes and such.

"""

import os
import pytest
from flask_sqlalchemy_session import flask_scoped_session

from sqlalchemy_pytest_fixtures import engine, session, session_factory, connection, schema_name

@pytest.fixture(scope='function')
def app(engine, session_factory):
    """ a flask app fixture
    """
    from pygameweb.app import create_app

    test_app = create_app('pygameweb.config.Config', engine, session_factory)

    return test_app


@pytest.fixture(scope='session')
def config():
    """ here we create our config and make sure we are using the test database.
    """
    from pygameweb.config import Config
    Config.SQLALCHEMY_DATABASE_URI = os.environ.get('APP_DATABASE_URL_TEST')
    Config.TESTING = True

    # do not send emails with flask-mail
    Config.MAIL_SUPPRESS_SEND = True

    # to make testing easier
    Config.WTF_CSRF_ENABLED = False

    return Config


@pytest.fixture(scope='session')
def get_metadata():
    """ returns a function which loads all the python models
        and returns a Base.metadata object.
    """
    def load_models():
        """ This is where we load all the models we want to test.
        """
        import pygameweb.models
        import pygameweb.wiki.models
        import pygameweb.user.models
        import pygameweb.project.models
        import pygameweb.page.models
        import pygameweb.news.models
        import pygameweb.doc.models
        import pygameweb.comment.models
        import pygameweb.tasks.models
        return pygameweb.models.metadata

    return load_models
