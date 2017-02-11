""" user models.


- use bcrypt
- in migration code, remove passwd field.



"""

from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, backref

from flask_security import (Security, SQLAlchemyUserDatastore,
                            UserMixin, RoleMixin, login_required)

from pygameweb.models import Base, metadata

# Define models
users_groups = Table(
    'users_groups', metadata,
    Column('users_id', Integer, ForeignKey('users.id', name='users_groups_users_id_fkey')),
    Column('groups_id', Integer, ForeignKey('groups.id', name='users_groups_groups_id_fkey'))
)

class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    email = Column(String(80))

    password = Column(String(255))
    """ new password field.
    """

    title = Column(String(80))
    disabled = Column(Integer, default=0)
    super = Column(Integer, default=0)

    roles = relationship('Group',
                         secondary=users_groups,
                         backref=backref('users', lazy='dynamic'))

    active = Column(Boolean())
    # https://flask-security-fork.readthedocs.io/en/latest/models.html#additional-functionality
    confirmed_at = Column(DateTime)

    last_login_at = Column(DateTime)
    current_login_at = Column(DateTime)
    last_login_ip = Column(String(80))
    current_login_ip = Column(String(80))
    login_count = Column(Integer)



class Group(Base, RoleMixin):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    title = Column(String(80))
    orders = Column(Integer)


    # https://flask-security-fork.readthedocs.io/en/latest/models.html#additional-functionality
    description = Column(String(80))

    def __str__(self):
        return f'{self.name}'
