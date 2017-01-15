""" Fixtures for flask and sqlalchemy with pytest.


Here you can see the nesting of transactions and db code as it happens.

    Creates an engine per pytest.session.
    Creates a connection per pytest.session.
        transaction
            create tables
                nested transaction
                    sqlalchemy.session
                        user test code.
"""

import pytest


from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


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


@pytest.fixture(scope='session')
def get_metadata():
    """ returns a function which loads all the python models
        and returns a Base.metadata object.
    """
    def load_models():
        """
        """
        raise NotImplementedError('you need to implement get_metadata.')

    return load_models


@pytest.fixture(scope='session')
def connection(request, engine, get_metadata):
    """ returns a db connection inside a transaction which rollsback when done.
    """
    a_connection = engine.connect()
    a_transaction = a_connection.begin()

    metadata = get_metadata()

    try:
        metadata.drop_all(a_connection)
    except SQLAlchemyError:
        pass

    metadata.create_all(a_connection)

    def teardown():
        """ cleanup
        """
        a_transaction.rollback()
        a_connection.close()

    request.addfinalizer(teardown)
    return a_connection


@pytest.fixture(scope='function')
def session_factory(request, connection):
    """ Creates a session within a transaction. Rolls back transaction when done.
    """
    transaction = connection.begin_nested()
    a_session_factory = sessionmaker(bind=connection)

    def final():
        """ Rollback.
        """
        transaction.rollback()

    request.addfinalizer(final)
    return a_session_factory


@pytest.fixture(scope='function')
def session(request, session_factory, connection):
    """ Returns a session, rollsback when done.
    """
    a_session = session_factory(bind=connection)

    def final():
        """ Rollback.
        """
        a_session.rollback()

    request.addfinalizer(final)
    return a_session

