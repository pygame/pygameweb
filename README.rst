Pieces of the pygame website will be open sourced here.

Issues https://bitbucket.org/pygame/pygame/issues?component=website

Strategy is to bring in code one piece at a time, and clean it up as I go.

The stack is something like: python 3.5, postgresql, Flask, py.test, sqlalchemy, alembic, gulp, ansible


TODO for db migration
=====================

- finish initial db migration from mysql to postgresql
- models missing some indexes (on tags etc)
- set up test framework and some fixtures
- port various queries to sqlalchemy
	- latest news, latest projects, add user, add release, projects for tags, etc
- generate db dump without private tables (user, etc)


Db setup instructions
=====================

createdb pygame
psql pygame -c "CREATE USER pygame WITH PASSWORD 'password';"
psql pygame -c "GRANT ALL PRIVILEGES ON DATABASE pygame to pygame;"
