Pieces of the pygame website will be open sourced here.

Issues https://bitbucket.org/pygame/pygame/issues?component=website

Strategy is to bring in code one piece at a time, and clean it up as I go.

The stack is something like: python 3.6, postgresql, Flask, py.test, sqlalchemy, alembic, gulp, ansible


Set up the required packages::

	virtualenv anenv
	. ./anenv/bin/activate
	pip install --upgrade pip
	pip install -r requirements.dev.txt


Db setup instructions
=====================

postgresql 9.6

We use alembic for db migrations. http://alembic.readthedocs.org/en/latest/


Set up the postgresql database::

	createdb pygame
	psql pygame -c "CREATE USER pygame WITH PASSWORD 'password';"
	psql pygame -c "GRANT ALL PRIVILEGES ON DATABASE pygame to pygame;"

We also create a database for running tests::

	createdb pygame_test
	psql pygame -c "CREATE USER pygame_test WITH PASSWORD 'password';"
	psql pygame_test -c "GRANT ALL PRIVILEGES ON DATABASE pygame_test to pygame_test;"


To upgrade to latest model changes do::

	alembic upgrade head


When you change a model make an alembic revision::

    alembic revision --autogenerate -m "Added a field for these reasons."



testing with py.test
====================

http://docs.pytest.org/en/latest/

To run all unit tests and functional tests use::

	py.test tests/functional/


tests/unit/ are for unit tests.
tests/functional/ are for tests which would use flask and db.
tests/conftest.py is for test configuration.
tests/conftest.py is for test configuration.
tests/sqlpytestflask.py are some fixtures for db testing.

