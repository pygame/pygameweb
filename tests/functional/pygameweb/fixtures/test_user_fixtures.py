import pytest

from pygameweb.fixtures import populate_db
from pygameweb.user.models import User, Group, users_groups


def test_populate_db(app, session):
    """ Ensures the populate_db adds sample data.
    """
    assert session.query(Group).count() == 0
    assert session.query(User).count() == 0

    app.config['DEBUG'] = True
    populate_db(make_app=lambda x: app)
    assert session.query(Group).count() == 5
    assert session.query(User).count() == 5

    # Makes sure the admin is really admin
    assert 1 == session.query(users_groups) \
                .filter_by(users_id=1, groups_id=5).count()


def test_populate_db_production(app, session):
    """ Ensures the populate_db won't work in production.
    """
    app.config['DEBUG'] = False
    with pytest.raises(RuntimeError):
        populate_db(make_app=lambda x: app)

    assert session.query(Group).count() == 0
    assert session.query(User).count() == 0
