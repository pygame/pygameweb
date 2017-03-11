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
    """order to be displayed in the navigation.
    """
    link = Column(String(255))
    """ link on the website we register for.
    """
    hidden = Column(Integer, default=0)
    """ hidden from the navigation.
    """
    uri = Column(String(255))
    """ uri to redirect to.
    """
    users_id = Column(Integer)
    groups_id = Column(Integer)
    nav_group = Column(String(255))
    """ A string if it is supposed to go in a navigation group.
    """
