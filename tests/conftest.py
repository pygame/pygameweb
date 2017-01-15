""" Fixtures for testing.

http://stackoverflow.com/questions/34466027/in-py-test-what-is-the-use-of-conftest-py-files

To make testing databases easier we need a few fixtures for rolling back changes and such.

"""


import os
import pytest

from sqlpytestflask import engine

@pytest.fixture(scope='function')
def app(engine):
    """ a flask app fixture
    """
    from pygameweb import create_app
    test_app = create_app('pygameweb.config.Config', engine)

    return test_app

@pytest.fixture(scope='session')
def config():
	""" here we create our config and make sure we are using the test database.
	"""
    import pygameweb.config
    pygameweb.config.Config.SQLALCHEMY_DATABASE_URI = os.environ.get('APP_DATABASE_URL_TEST')
    pygameweb.config.Config.TESTING = True

    return pygameweb.config.Config

