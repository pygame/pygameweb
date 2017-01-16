"""Fixtures for sqlalchemy, postgesql, flask with pytest.

The benefits for these are they can::

    * makes writing sql tests easy, fast, and robust.
    * Run in parallel, in separate schemas per connection.
    * Only create the tables once for each pytest session.

Example::

    >>> def test_bla(session):
            from bla.models import Bla
            bla = Bla(name="hell")
            assert bla.name == 'hell'
            session.add(bla)
            session.commit()


Here you can see the nesting of transactions and db code as it happens.

    Creates an engine per pytest.session.
    Creates a connection per pytest.session.
        transaction
            create unique schema for these tests
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
def schema_name():
    """ Returns a schema name.
    """
    import uuid
    return uuid.uuid4()


@pytest.fixture(scope='session')
def connection(request, engine, get_metadata, schema_name):
    """ returns a db connection inside a transaction which rollsback when done.
    """
    a_connection = engine.connect()
    a_transaction = a_connection.begin()

    # Make a schema for tests to run in.
    # We are in a transaction so this is rolled back too.
    a_connection.execute('CREATE SCHEMA "%s"' % schema_name)
    # Set the schema search_path, so we use the new schema.
    a_connection.execute('SET search_path TO "%s"' % schema_name)

    metadata = get_metadata()

    try:
        metadata.drop_all(a_connection)
    except SQLAlchemyError:
        pass

    # make all the tables
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

