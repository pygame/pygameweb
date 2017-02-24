"""For setting up navigation.

http://pythonhosted.org/flask-nav/
https://pythonhosted.org/Flask-Bootstrap/nav.html
"""

from flask_sqlalchemy_session import current_session
from pygameweb.page.models import Page


from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, Link

def make_nav(session):
    """ Creates the navigation using flask-nav.
    """
    pages = (session
             .query(Page)
             .filter(Page.link != '')
             .filter(Page.hidden == 0)
             .order_by(Page.orders)
             .all())

    parts = []
    groups = {}

    for page in pages:
        dest = '/' + page.link if page.uri is None else page.uri
        # add all pages with the same nav_group into a Subgroup.
        if page.nav_group:
            if page.nav_group not in groups:
                groups[page.nav_group] = Subgroup(page.nav_group)
                parts.append(groups[page.nav_group])
            groups[page.nav_group].items.append(Link(page.name, dest))
        else:
            parts.append(Link(page.name, dest))

    nav_bar = Navbar('pygame')
    nav_bar.items.extend(parts)
    return nav_bar


def add_nav(app):
    """ called by pygameweb.app.add_views_front
    """
    nav = Nav()

    @nav.navigation()
    def mynavbar():
        """ Every time a page is loaded we create the navigation.
        """
        return make_nav(current_session)

    nav.init_app(app)
