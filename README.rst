Pieces of the pygame website will be open sourced here.

Issues https://bitbucket.org/pygame/pygame/issues?component=website

Strategy is to bring in code one piece at a time, and clean it up as I go.

The stack is something like: python 3.5, postgresql, Flask, py.test, sqlalchemy, alembic, gulp, ansible


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


To upgrade to latest model changes do::

	alembic upgrade head


When you change a model make an alembic revision::

    alembic revision --autogenerate -m "Added a field for these reasons."



testing
=======

We use py.test for testing.

http://docs.pytest.org/en/latest/

