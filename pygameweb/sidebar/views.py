""" Sneak that sidebar stuff into our views.

Side bar stuff includes::

    * recent releases
    * project tags
"""

from flask_sqlalchemy_session import current_session
from pygameweb.project.models import top_tags, recent_releases
from pygameweb.user.models import User


def sidebar():
    """ called by template in base.html sidebar block.
    """
    return dict(
      top_tag_counts=top_tags(current_session),
      recent_releases=(recent_releases(current_session)
                       .limit(10)
                       .all())
    )


def add_sidebar(app):
    """ to the app.
    """
    app.add_template_global(sidebar, 'sidebar')
