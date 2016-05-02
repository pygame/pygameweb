""" Page related models.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, text, LargeBinary
from pygameweb.models import Base


class Module(Base):
    __tablename__ = 'modules'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    title = Column(String(80))
    orders = Column(Integer)


class Node(Base):
    __tablename__ = 'node'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    title = Column(String(255))
    keywords = Column(String(255))
    type = Column(String(255))
    content = Column(Text)
    summary = Column(Text)
    orders = Column(Integer, nullable=False, default=0)
    parentid = Column(Integer)
    link = Column(String(255))
    hidden = Column(Integer, default=0)
    target = Column(String(80))
    custom = Column(LargeBinary)
    skin_id = Column(Integer)
    uri = Column(String(255))
    users_id = Column(Integer)
    groups_id = Column(Integer)
    mods = Column(Integer)
    folderid = Column(Integer)
    folder = Column(Integer, default=0)
    modules_id = Column(Integer)
    image = Column(String(255))


class Skin(Base):
    __tablename__ = 'skin'

    id = Column(Integer, primary_key=True)
    title = Column(String(80))
    fname = Column(String(80))
    orders = Column(Integer)
