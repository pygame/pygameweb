""" News related models.
"""

import datetime

from sqlalchemy import (
    Column, DateTime, Integer, String, Text, text,
    LargeBinary, UniqueConstraint, Index
)
from slugify import slugify
from email.utils import formatdate

from pygameweb.models import Base

from pygameweb.sanitize import sanitize_html



def slugify_title(title, datetimeon):
    """ creates a link slug based on the date and the title.
    """
    year, month = datetimeon.year, datetimeon.month
    the_slug_start = f'{year}/{month}/'
    max_length = 200 - len(the_slug_start)
    return the_slug_start + slugify(title, max_length=max_length)


class News(Base):
    __tablename__ = 'news'

    def __init__(
        self,
        title,
        description,
        summary,
        id=None,
        datetimeon=None,
        submit_users_id=None,
        slug=None
    ):
        """
        :param str title: of the news post.
        :param str description: is the body text of the news post.
        :param int id: of the news item.
        :param datetimeon: when the thing was published.
        :param int submit_users_id: that posted this thing.
        :param str slug: the url link for this news item.
        """
        self.title = title
        self.description = description
        self.summary = summary
        self.id = id
        self.datetimeon = datetime.datetime.utcnow() if datetimeon is None else datetimeon
        self.submit_users_id = submit_users_id
        self.slug = slugify_title(title, datetimeon) if slug is None else slug

    id = Column(Integer, primary_key=True)
    title = Column(String(80))
    description = Column(Text)
    summary = Column(String(140))
    """ A 140 character summary of the news.
    """

    datetimeon = Column(DateTime)
    submit_users_id = Column(Integer)
    slug = Column(String(200), nullable=False, unique=True)
    """ the link slug for the news item.
    """

    __table_args__ = (
        UniqueConstraint('slug', name='news_slug_key'),
        Index('ix_news_slug', 'slug', unique=True),
    )

    @property
    def title_html(self):
        return sanitize_html(self.title)

    @property
    def description_html(self):
        return sanitize_html(self.description)

    @property
    def datetimeon_2882(self):
        return formatdate(self.datetimeon.timestamp())


class NewsAlert(Base):
    __tablename__ = 'news_alert'

    def __init__(
        self,
        title,
        description,
        summary,
        id=None,
        datetimeon=None,
        submit_users_id=None,
        slug=None
    ):
        """
        :param str title: of the news post.
        :param str description: is the body text of the news post.
        :param int id: of the news item.
        :param datetimeon: when the thing was published.
        :param int submit_users_id: that posted this thing.
        :param str slug: the url link for this news item.
        """
        self.title = title
        self.description = description
        self.summary = summary
        self.id = id
        self.datetimeon = datetime.datetime.utcnow() if datetimeon is None else datetimeon
        self.submit_users_id = submit_users_id
        self.slug = slugify_title(title, datetimeon) if slug is None else slug
    id = Column(Integer, primary_key=True)
    title = Column(String(80))
    description = Column(Text)
    summary = Column(String(140))
    """ A 140 character summary of the news.
    """

    datetimeon = Column(DateTime)
    submit_users_id = Column(Integer)
    slug = Column(String(200), nullable=False, unique=True)
    """ the link slug for the news item.
    """

    __table_args__ = (
        UniqueConstraint('slug', name='news_alert_slug_key'),
        Index('ix_news_alert_slug', 'slug', unique=True),
    )

    @property
    def title_html(self):
        return sanitize_html(self.title)

    @property
    def description_html(self):
        return sanitize_html(self.description)

    @property
    def datetimeon_2882(self):
        return formatdate(self.datetimeon.timestamp())
