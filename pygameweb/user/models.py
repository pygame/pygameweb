""" user models.
"""

from sqlalchemy import Column, Integer, String, Table
from pygameweb.models import Base, metadata


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    email = Column(String(80))
    passwd = Column(String(80))
    title = Column(String(80))
    disabled = Column(Integer, default=0)
    super = Column(Integer, default=0)


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    title = Column(String(80))
    orders = Column(Integer)


t_users_groups = Table(
    'users_groups', metadata,
    Column('users_id', Integer),
    Column('groups_id', Integer)
)
