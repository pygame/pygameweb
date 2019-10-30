""" models for projects
"""
from math import sqrt
from pathlib import Path
from email.utils import formatdate
from urllib.parse import urlparse, parse_qs, urlencode

from sqlalchemy import (Column, DateTime, ForeignKey, Integer,
                        String, Text, inspect, func, and_, or_, CheckConstraint)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql.functions import count

from pyquery import PyQuery as pq

from pygameweb.models import Base
from pygameweb.user.models import User
from pygameweb.config import Config
from pygameweb.thumb import image_thumb
from pygameweb.sanitize import sanitize_html


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer,
                      ForeignKey(User.id, name='project_user_id_fkey'),
                      nullable=False)

    node_id = Column(Integer)
    title = Column(String(80))
    summary = Column(Text)
    description = Column(Text)
    uri = Column(String(255))
    datetimeon = Column(DateTime)
    image = Column(String(80))

    github_repo = Column(Text)
    """ URL to the github repo for this project.
    """
    _github_repo_constraint = CheckConstraint(
        or_(
            github_repo is None,
            github_repo == '',
            github_repo.startswith('https://github.com/')
        ),
        name="project_github_repo_constraint"
    )


    youtube_trailer = Column(Text)
    """ URL to the youtube trailer for this project.
    """
    _youtube_trailer_constraint = CheckConstraint(
        or_(
            youtube_trailer is None,
            youtube_trailer == '',
            youtube_trailer.startswith('https://www.youtube.com/watch?v=')
        ),
        name="project_youtube_trailer_constraint"
    )

    patreon = Column(Text)
    """ URL to the patreon.
    """
    _patreon_constraint = CheckConstraint(
        or_(
            patreon is None,
            patreon == '',
            patreon.startswith('https://www.patreon.com/')
        ),
        name="project_patreon_constraint"
    )


    def __repr__(self):
        return "<Project with title=%r>" % self.title

    @property
    def summary_html(self):
        return sanitize_html(self.summary)

    @property
    def summary_html_text(self):
        return pq(self.summary_html).text()

    @property
    def description_html(self):
        return sanitize_html(self.description)

    def image_thumb(self, width, height):
        """ Return path to the thumbnail for this image.
        """
        return image_thumb(Path(Config.WWW), self.image, width, height)

    # tags = relationship(Tags, backref='projects')
    user = relationship(User, backref='projects')

    @property
    def tag_counts(self):
        """ Return a list of counts for the tags this project has.

        [('arcade', 2), ('opengl', 1)]
        """

        tags = [t.value for t in self.tags]
        cnt = count(Tags.value)

        tag_counts = (inspect(self).session
                      .query(Tags.value, cnt)
                      .group_by(Tags.value)
                      .filter(Tags.value.in_(tags))
                      .order_by(cnt.desc())).all()
        return [(tag, cnt, (int(10 + min(24, sqrt(cnt) * 24 / 5))))
                for tag, cnt in tag_counts]

    @property
    def youtube_trailer_embed(self):
        if not self.youtube_trailer:
            return
        video_key = parse_qs(urlparse(self.youtube_trailer).query).get('v')
        if not video_key:
            return
        bad_chars = ['?', ';', '&', '..', '/']
        if any(bad in video_key[0] for bad in bad_chars):
            raise ValueError('problem')
        return f'http://www.youtube.com/embed/{video_key[0]}'

    __table_args__ = (
        _github_repo_constraint,
        _youtube_trailer_constraint,
        _patreon_constraint,
    )


def top_tags(session, limit=30):
    """
    """
    cnt = count(Tags.value)

    tag_counts = (session
                  .query(Tags.value, cnt)
                  .group_by(Tags.value)
                  .order_by(cnt.desc())
                  .limit(limit)).all()
    return [(tag, cnt, (int(10 + min(24, sqrt(cnt) * 24 / 5))))
            for tag, cnt in tag_counts]


class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer,
                        ForeignKey(Project.id, name='tags_project_id_fkey'),
                        nullable=False,
                        index=True)
    value = Column('value', String(32), index=True)
    project = relationship(Project, backref='tags')


class Projectcomment(Base):
    __tablename__ = 'projectcomment'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer,
                        ForeignKey(Project.id,
                                   name='projectcomment_project_id_fkey'),
                        nullable=False)
    users_id = Column(Integer,
                      ForeignKey(User.id, name='projectcomment_users_id_fkey'),
                      nullable=False)

    datetimeon = Column(DateTime)
    content = Column(Text)
    rating = Column(Integer)

    project = relationship(Project, backref='comments')
    user = relationship(User, backref='projectcomments')


def recent_releases(session):
    """
    """
    releases = session.query(
        Release.project_id,
        func.max(Release.datetimeon).label('max_datetimeon'),
    ).group_by(Release.project_id).subquery('releases')

    query = (session
      .query(User, Project, Release)
      .filter(and_(Project.id == Release.project_id,
              Project.id == releases.c.project_id,
              Release.datetimeon == releases.c.max_datetimeon))
      .filter(User.id == Project.users_id)
      .filter(User.disabled == 0)
      .order_by(Release.datetimeon.desc())
    )
    return query


class Release(Base):
    __tablename__ = 'release'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer,
                        ForeignKey(Project.id, name='release_project_id_fkey'),
                        nullable=False)

    datetimeon = Column(DateTime)
    description = Column(Text)
    srcuri = Column(String(255))
    winuri = Column(String(255))
    macuri = Column(String(255))
    version = Column(String(80))

    from_external = Column(String(255))
    """ is this release sucked in from an external source.

        If it is 'github' then it comes from a github release.
        If it is None, then it is user entered.
    """

    project = relationship(Project, backref='releases')

    @property
    def datetimeon_2882(self):
        return formatdate(self.datetimeon.timestamp())

    @property
    def description_html(self):
        return sanitize_html(self.description)
