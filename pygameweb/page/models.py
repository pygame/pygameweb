""" Page related models.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, text, LargeBinary
from pygameweb.models import Base


class Page(Base):
    __tablename__ = 'page'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    title = Column(String(255))
    keywords = Column(String(255))
    content = Column(Text)
    summary = Column(Text)
    orders = Column(Integer, nullable=False, default=0)
    link = Column(String(255))
    hidden = Column(Integer, default=0)
    uri = Column(String(255))
    users_id = Column(Integer)
    groups_id = Column(Integer)
