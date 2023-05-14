pygame.org website |coverage-status|
====================================

Pieces of the pygame website (https://www.pygame.org/) will be open sourced here.

Strategy is to bring in code one piece at a time, and clean it up as I go.


It's a community website where people can post projects, comment on them,
but also write things in there themselves on wiki pages.


Quick-Start
===========

Set up the required packages::

    python3.6 -m venv anenv
    . ./anenv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.dev.txt
    pip install -e .

If you would get some error related to *pip's conflict checker update* after execute **pip install -r requirements.dev.txt**, add the flag **--use-feature=2020-resolver** to the end of the command.

For now yuicompressor is needed for css compression, and
imagamagick and optipng are needed for creating and optimizing image thumbnails,
additionally postgresql is the database of choice::
    brew install yuicompressor node optipng imagemagick postgresql
    sudo apt-get install yui-compressor nodejs optipng imagemagick postgresql postgresql-client libpq-dev


Environment setup
=================

Define a **.env** file based on the **example.env** file.

::

    cp example.env .env

Define the **APP_SECRET_KEY** variable in the **.env** file or the tests won't work. 
You can define any value, like **"a"** or **"s3cret-stuff-blah"**.

Tool setup
==========

See setup.cfg for all tool config (pytest, coverage, etc).



Db setup instructions
=====================

postgresql 9.6

One database for testing, and another one for running the app.

We use alembic for db migrations. http://alembic.readthedocs.org/en/latest/


Set up the `postgresql` database:

    sudo -u postgres createdb pygame
    sudo -u postgres psql pygame -c "CREATE USER pygame WITH PASSWORD 'password';"
    sudo -u postgres psql pygame -c "GRANT ALL PRIVILEGES ON DATABASE pygame to pygame;"

We also create a database for running tests::

    sudo -u postgres createdb pygame_test
    sudo -u postgres psql pygame -c "CREATE USER pygame_test WITH PASSWORD 'password';"
    sudo -u postgres psql pygame_test -c "GRANT ALL PRIVILEGES ON DATABASE pygame_test to pygame_test;"


To upgrade to latest model changes do::

    alembic upgrade head


When you change a model make an alembic revision::

    alembic revision --autogenerate -m "Added a field for these reasons."

Then you will need to apply the change to your db (and commit the version file)::

    alembic upgrade head


Testing with pytest
===================

http://docs.pytest.org/en/latest/

To run all unit tests and functional tests use::

    pytest

To watch for changes and rerun tests::

    ptw

Maybe you just want to test the wiki parts::

    pytest -k wiki


tests/unit/ are for unit tests.
tests/functional/ are for tests which would use flask and db.
tests/conftest.py is for test configuration.
tests/sqlpytestflask.py are some fixtures for db testing.

Unit tests and functional tests are kept separate, because functional tests can take a while longer to run.

We use various fixtures to make writing the tests easier and faster.


Running the webserver locally
=============================

Use an environment variable to configure the database connection (see the
database setup steps above)::

    export APP_DATABASE_URL="postgresql://pygame:password@localhost/pygame"

Configure a directory containing static files::

    export APP_WWW="static/"

The application may need a secure key, but for debugging it's not important
that it's properly random::

    export APP_SECRET_KEY="s3cret-stuff-blah"

Finally, you can enable some Flask debugging machinery (which should be off for
the site in production)::

    export APP_DEBUG=1

Now add the database fixtures to populate it with sample users. After that, you should be able to
login as admin with email ``admin@example.com`` and  password ``password``::
    
    pygameweb_fixtures
    
Then run::

    pygameweb_front


Templates with jinja2 and bootstrap
===================================

pygameweb/templates/

We use::

    * `Jinja2 <http://jinja.pocoo.org/>`_
    * `Flask-Bootstrap <https://pythonhosted.org/Flask-Bootstrap/basic-usage.html>`_
    * `Bootstrap <http://getbootstrap.com/>`_


Command line tools with click
=============================

We use click and setuptools entry points (in setup.py) for command line tools::

    * `click <http://click.pocoo.org/5/>`_
    * `entry points <https://packaging.python.org/distributing/#entry-points>`_

Note, when you add or change a command line tool, you need to `pip install -e .` again.

If you can, try not to use command line options at all. Have one command do one thing,
and make the defaults good, or use the pygameweb.config.


User login with Flask-security-fork
===================================

pygameweb.user
pygameweb/templates/security

Using::

    * `flask-security-fork <https://flask-security-fork.readthedocs.io/en/latest/quickstart.html>`_


Navigation with flask-nav
=========================

pygameweb.nav
pygameweb.page.models

Using::

    * `flask-nav <http://pythonhosted.org/flask-nav/>`_
    * `flask-bootstrap <https://pythonhosted.org/Flask-Bootstrap/nav.html>`_



Dashboard is an overview
========================

of all sorts of things happening in the pygame worlds around the interwebs.

https://pygame.org/dashboard

It's a 7000px wide webpage offering a summary of what's happening.

Projects people are working on,
videos folks are making,
tweets twits are... tweeting,
questions asked and answered.



To caching things we
====================

use `Flask-Caching <http://pythonhosted.org/Flask-Caching/>`_

pygameweb.cache
pygameweb.news.views


With with a @cache decorator, and/or markup in a template.


.. |coverage-status| image:: https://coveralls.io/repos/github/pygame/pygameweb/badge.svg?branch=main
   :target: https://coveralls.io/github/pygame/pygameweb?branch=main
   :alt: Test coverage percentage



Releases
========

Step by step release instructions below.

- Commits to `main` branch do a dev deploy to pypi.
- Commits to `maintest` branch do a dev deploy to pypi.
- Commits to a tag do a real deploy to pypi.


Prereleases
-----------

https://packaging.python.org/tutorials/distributing-packages/#pre-release-versioning

Pre releases should be named like this:
```
# pygameweb/__init__.py
__version__ = '0.0.2'
```
Which is one version ahead of of the last tagged release.

Release tags should be like '0.0.2', and match the `pygameweb/__init__.py __version__`.


Preparing a release in a branch.
--------------------------------

It's a good idea to start a branch first, and make any necessary changes
for the release.

```
git checkout -b v0.0.2
vi pygameweb/__init__.py __version__ = '0.0.2'
git commit -m "Version 0.0.2"
```

Change log, drafting a release.
-------------------------------

Github 'releases' are done as well.
You can start drafting the release notes in there before the tag.
https://help.github.com/articles/creating-releases/

You can make the release notes with the help of the changes since last release.
https://github.com/pygame/pygameweb/compare/0.0.1...main

git log 0.0.1...main

Tagging a release
-----------------

When the release is tagged, pushing it starts the deploy to pypi off.
```
git tag -a 0.0.2
git push origin 0.0.2
```
Note: do not tag pre releases
(these are made on commits to `main`/`maintest`).

After the tag is pushed, then you can do the release
in github from your draft release.


Back to dev version.
--------------------

If we were at 0.0.2 before, now we want to be at 0.0.3.dev
```
vi pygameweb/__init__.py __version__ = '0.0.3.dev'
```

Merge the release branch into main, and push that up.


Contributing
============

Please discuss contributions first to avoid disappointment and rework.

Please see `contribution-guide.org <http://www.contribution-guide.org/>`_ and
`Python Code of Conduct <https://www.python.org/psf/codeofconduct/>`_ for
details on what we expect from contributors. Thanks!

The stack? python 3.6, postgresql 9.6, Flask, py.test, sqlalchemy, alembic, gulp, ansible, node.
