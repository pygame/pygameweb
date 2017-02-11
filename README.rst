Pieces of the pygame website will be open sourced here.

Issues https://bitbucket.org/pygame/pygame/issues?component=website

Strategy is to bring in code one piece at a time, and clean it up as I go.

The stack is something like: python 3.6, postgresql, Flask, py.test, sqlalchemy, alembic, gulp, ansible, node.


Set up the required packages::

    virtualenv anenv
    . ./anenv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.dev.txt
    pip install -e .


For now yuicompressor is needed for css compression::

    brew install yuicompressor node
    apt-get install yui-compressor node


Environment setup
=================

cp example.env .env



Db setup instructions
=====================

postgresql 9.6

One database for testing, and another one for running the app.

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

Then you will need to apply the change to your db (and commit the version file)::

    alembic upgrade head


testing with py.test
====================

http://docs.pytest.org/en/latest/

To run all unit tests and functional tests use::

    py.test tests/functional/


tests/unit/ are for unit tests.
tests/functional/ are for tests which would use flask and db.
tests/conftest.py is for test configuration.
tests/sqlpytestflask.py are some fixtures for db testing.

Unit tests and functional tests are kept separate, because functional tests can take a while longer to run.

We use various fixtures to make writing the tests easier and faster.


Templates with jinja2 and bootstrap
===================================

We use::

    * Jinja2 http://jinja.pocoo.org/
    * Flask-Bootstrap https://pythonhosted.org/Flask-Bootstrap/basic-usage.html
    * Bootstrap http://jinja.pocoo.org/


Command line tools with click
=============================

We use click and setuptools entry points (in setup.py) for command line tools.

* click http://click.pocoo.org/5/
* entry points https://packaging.python.org/distributing/#entry-points

Note, when you add or change a command line tool, you need to `pip install -e .` again.



User login with Flask-security-fork
===================================

https://flask-security-fork.readthedocs.io/en/latest/quickstart.html





