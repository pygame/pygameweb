""" News related models.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, text, LargeBinary
from pygameweb.models import Base

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    title = Column(String(80))
    description = Column(Text)
    datetimeon = Column(DateTime)
    submit_users_id = Column(Integer)

