""" Documentation related models. Mainly comments.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, text
from pygameweb.models import Base

class Docscomment(Base):
    __tablename__ = 'docscomment'

    id = Column(Integer, primary_key=True)
    link = Column(String(255))
    users_id = Column(Integer)
    datetimeon = Column(DateTime)
    content = Column(Text)
