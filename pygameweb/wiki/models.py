""" wiki models
"""

from sqlalchemy import Column, DateTime, Integer, String, Text
from pygameweb.models import Base

class Wiki(Base):
    __tablename__ = 'wiki'

    id = Column(Integer, primary_key=True, default=0)
    link = Column(String(255))
    summary = Column(Text)
    content = Column(Text)
    datetimeon = Column(DateTime)
    fname = Column(String(255))
    changes = Column(String(255))
    users_id = Column(Integer)
    latest = Column(Integer)
    name = Column(String(255))
    title = Column(String(255))
    parent = Column(String(255))
    keywords = Column(String(255))
