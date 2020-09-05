""" Populates the database with sample data
"""
import yaml
from flask_sqlalchemy_session import current_session

from pygameweb.user.models import User, Group
from pygameweb.app import create_app


def _user_fixtures(fixture='pygameweb/user/fixtures/fixtures.yml'):
    """ Adds user fixtures.
    """
    with open(fixture, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    current_session.bulk_insert_mappings(Group, data['groups'])
    current_session.bulk_insert_mappings(User, data['users'])
    current_session.commit()

    # Apply roles to users
    for user_data in data['users']:
        user = current_session.query(User).get(user_data['id'])
        for role in user_data['roles']:
            group = current_session.query(Group) \
                                   .filter_by(name=role).first()
            user.roles.append(group)
        current_session.add(user)
    current_session.commit()


# Note: `make_app` is used in tests.fixtures for testing
def populate_db(make_app=create_app):
    """ Adds fixtures to database. Useful for testing locally.
    """
    app = make_app('pygameweb.config.Config')
    # Avoid accidentally running this in production
    if not app.debug:
        raise RuntimeError('Please enable debug. ' +
                           'Are you running in production?')
    with app.app_context():
        _user_fixtures()
    app.logger.info('Fixtures added to database.')
