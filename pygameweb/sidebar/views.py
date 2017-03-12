""" Sneak that sidebar stuff into our views.

Side bar stuff includes::

    * recent releases
    * project tags
"""

from flask_sqlalchemy_session import current_session
from pygameweb.project.models import top_tags, Project, Release
from pygameweb.user.models import User


def sidebar():
    """ called by template in base.html sidebar block.
    """
    top_tag_counts = top_tags(current_session)

    recent_releases = (current_session.query(User, Project, Release)
                       .filter(Release.project_id == Project.id)
                       .filter(User.id == Project.users_id)
                       .filter(User.disabled == 0)
                       .order_by(Release.datetimeon.desc())
                       .limit(10)
                       .all())
    return dict(top_tag_counts=top_tag_counts, recent_releases=recent_releases)


def add_sidebar(app):
    """ to the app.
    """
    app.add_template_global(sidebar, 'sidebar')
