""" wiki models
"""
import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String,
    Text, ForeignKey, inspect
)
from sqlalchemy.orm.session import make_transient
from sqlalchemy.orm import relationship

from pygameweb.models import Base
from pygameweb.wiki.wiki import render, render_pq
from pygameweb.user.models import User
from pygameweb.sanitize import sanitize_html


class Wiki(Base):
    """ Each entry is a wiki page.
    """
    __tablename__ = 'wiki'

    id = Column(Integer, primary_key=True)
    link = Column(String(255))
    summary = Column(Text)
    content = Column(Text)
    datetimeon = Column(DateTime)
    fname = Column(String(255))
    changes = Column(String(255))
    latest = Column(Integer)
    name = Column(String(255))
    title = Column(String(255))
    parent = Column(String(255))
    keywords = Column(String(255))

    locked = Column(Boolean)
    """ True if only an admin user can edit it. """

    users_id = Column(Integer,
                      ForeignKey(User.id,
                                 name='wiki_user_id_fkey'),
                      nullable=True)
    user = relationship(User)

    @classmethod
    def content_for_link(cls, session, link):
        """ returns the page content for the link.
        """
        page = cls.content_for_link(session, link)
        return '' if page is None else page.content

    @classmethod
    def for_link(cls, session, link):
        """ returns a wiki instance for the link given.
        """
        return (session
                .query(cls)
                .filter(cls.link == link)
                .filter(cls.latest == 1)
                .first())

    def new_version(self, session):
        """ Create a new version of this page. Leave the old on in the db.
        """
        session.begin_nested()

        self.latest = 0
        session.add(self)
        session.commit()

        # this makes sqlalchemy forget about this object. In effect copying it.
        session.expunge(self)
        # http://docs.sqlalchemy.org/en/rel_1_1/orm/session_api.html#sqlalchemy.orm.session.make_transient
        make_transient(self)

        del self.id
        self.latest = 1
        self.datetimeon = datetime.datetime.now()
        session.add(self)

    @property
    def content_rendered(self):
        """The wiki content is rendered for display.
        """
        session = inspect(self).session

        def for_link(link):
            return Wiki.content_for_link(session, link)

        return sanitize_html(render(self.content, for_link))

    @property
    def content_toc(self):
        """The wiki content is rendered for display.
        """
        session = inspect(self).session

        def for_link(link):
            return Wiki.content_for_link(session, link)

        if not self.content:
            return '', ''
        content, toc = render_pq(self.content, for_link, toc_separate=True)
        return (sanitize_html(content.outerHtml() if content is not None else ''),
                sanitize_html(toc.outerHtml() if toc is not None else ''))


    @property
    def content_sanitized(self):
        """The wiki content which has any html sanitized.
        """
        return sanitize_html(self.content)
