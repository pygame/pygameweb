""" News related models.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, text, LargeBinary
from pygameweb.models import Base

from pygameweb.sanitize import sanitize_html
from email.utils import formatdate

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    title = Column(String(80))
    description = Column(Text)
    datetimeon = Column(DateTime)
    submit_users_id = Column(Integer)

    @property
    def title_html(self):
        return sanitize_html(self.title)

    @property
    def description_html(self):
        return sanitize_html(self.description)

    @property
    def datetimeon_2882(self):
        return formatdate(self.datetimeon.timestamp())
