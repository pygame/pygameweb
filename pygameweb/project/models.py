""" models for projects
"""

from sqlalchemy import Column, DateTime, Integer, String, Table, Text
from pygameweb.models import Base, metadata


t_tags = Table(
    'tags', metadata,
    Column('project_id', Integer, index=True),
    Column('value', String(32), index=True)
)


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer)
    node_id = Column(Integer)
    title = Column(String(80))
    summary = Column(Text)
    description = Column(Text)
    uri = Column(String(255))
    datetimeon = Column(DateTime)
    image = Column(String(80))


class Projectcomment(Base):
    __tablename__ = 'projectcomment'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    users_id = Column(Integer)
    datetimeon = Column(DateTime)
    content = Column(Text)
    rating = Column(Integer)


class Release(Base):
    __tablename__ = 'release'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    datetimeon = Column(DateTime)
    description = Column(Text)
    srcuri = Column(String(255))
    winuri = Column(String(255))
    macuri = Column(String(255))
    title = Column(String(80))
