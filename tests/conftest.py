""" Fixtures for testing.

http://stackoverflow.com/questions/34466027/in-py-test-what-is-the-use-of-conftest-py-files

To make testing databases easier we need a few fixtures for rolling back changes and such.

"""


import os
import pytest


@pytest.fixture(scope='function')
def app():
    """ a flask app fixture
    """
    import pygameweb.config
    from pygameweb import create_app


    pygameweb.config.Config.SQLALCHEMY_DATABASE_URI = os.environ.get('APP_DATABASE_URL_TEST')
    pygameweb.config.Config.TESTING = True
    test_app = create_app('pygameweb.config.Config')

    return test_app
