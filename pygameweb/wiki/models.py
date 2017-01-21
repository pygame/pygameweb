""" wiki models
"""

from sqlalchemy import Column, DateTime, Integer, String, Text
import feedparser
from pygameweb.models import Base


from pygameweb.wiki.wiki import render


def sanitize_html(html):
    """ santise_html(html) returns some sanitized html.
          It can be used to try and avoid basic html insertion attacks.

        >>> sanitize_html("<p>hello</p>")
        '<p>hello</p>'
        >>> sanitize_html("<script>alert('what')</script>")
        ''
    """
    return feedparser._sanitizeHTML(html, "utf-8", "text/html")


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

    @property
    def content_rendered(self):
        """The wiki content is rendered for display.
        """
        return sanitize_html(render(self.content))

    @property
    def content_sanitized(self):
        """The wiki content which has any html sanitized.
        """
        return sanitize_html(self.content)
