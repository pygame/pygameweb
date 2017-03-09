""" models for projects
"""
from math import sqrt
from pathlib import Path
from email.utils import formatdate

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, inspect
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import count

from pygameweb.models import Base, metadata
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


    @property
    def summary_html(self):
        return sanitize_html(self.summary)

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
        """ Return a list of counts for the tags this project has. [('arcade', 2), ('opengl', 1)]
        """

        tags = [t.value for t in self.tags]
        cnt = count(Tags.value)

        tag_counts = (inspect(self).session
                      .query(Tags.value, cnt)
                      .group_by(Tags.value)
                      .filter(Tags.value.in_(tags))
                      .order_by(cnt.desc())).all()
        return [(tag, cnt, (int(10+min(24, sqrt(cnt)*24/5)))) for tag, cnt in tag_counts]


def top_tags(session):
    """
    """
    cnt = count(Tags.value)

    tag_counts = (session
                  .query(Tags.value, cnt)
                  .group_by(Tags.value)
                  .order_by(cnt.desc())
                  .limit(30)).all()
    return [(tag, cnt, (int(10+min(24, sqrt(cnt)*24/5)))) for tag, cnt in tag_counts]




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
                        ForeignKey(Project.id, name='projectcomment_project_id_fkey'),
                        nullable=False)
    users_id = Column(Integer,
                      ForeignKey(User.id, name='projectcomment_users_id_fkey'),
                      nullable=False)


    datetimeon = Column(DateTime)
    content = Column(Text)
    rating = Column(Integer)

    project = relationship(Project, backref='comments')
    user = relationship(User, backref='projectcomments')


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

    project = relationship(Project, backref='releases')

    @property
    def datetimeon_2882(self):
        return formatdate(self.datetimeon.timestamp())

