"""Fixtures for flask and sqlalchemy with pytest.
"""

import pytest


from sqlalchemy import create_engine

@pytest.fixture(scope='session')
def engine(config):
    """ creates an sqlalchemy engine.
    """
    an_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    return an_engine


@pytest.fixture(scope='session')
def config():
    """ returns a flask config class.
    """
    return object

