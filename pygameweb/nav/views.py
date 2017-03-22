"""For setting up navigation.

http://pythonhosted.org/flask-nav/
https://pythonhosted.org/Flask-Bootstrap/nav.html
"""

from flask_sqlalchemy_session import current_session
from pygameweb.page.models import Page

from flask import url_for
from werkzeug.routing import BuildError
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, Link, View


# hackity hack the navbar...
from hashlib import sha1
from dominate import tags

import flask_bootstrap.nav
BootstrapRendererOld = flask_bootstrap.nav.BootstrapRenderer


class BootstrapRendererNew(BootstrapRendererOld):
    """ We have to hack this to add an image.

    Should probably just do the navigation ourselves.
    """

    def visit_Navbar(self, node):
        # create a navbar id that is somewhat fixed, but do not leak any
        # information about memory contents to the outside
        node_id = self.id or sha1(str(id(node)).encode()).hexdigest()

        root = tags.nav() if self.html5 else tags.div(role='navigation')
        root['class'] = 'navbar navbar-default'

        cont = root.add(tags.div(_class='container-fluid'))

        # collapse button
        header = cont.add(tags.div(_class='navbar-header'))
        btn = header.add(tags.button())
        btn['type'] = 'button'
        btn['class'] = 'navbar-toggle collapsed'
        btn['data-toggle'] = 'collapse'
        btn['data-target'] = '#' + node_id
        btn['aria-expanded'] = 'false'
        btn['aria-controls'] = 'navbar'

        btn.add(tags.span('Toggle navigation', _class='sr-only'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))

        # title may also have a 'get_url()' method, in which case we render
        # a brand-link
        if node.title is not None:
            if hasattr(node.title, 'get_url'):
                # a_tag = tags.a(node.title.text, _class='navbar-brand',
                #                   href=node.title.get_url())
                style = 'max-width:100px;margin-top: 18px;margin-right: 4px;'
                header.add(tags.span('pip install',
                                     _class='navbar-left hidden-xs',
                                     style=style))
                a_tag = tags.a(_class='navbar-left',
                               title=node.title.text,
                               href=node.title.get_url())
                a_tag.add(tags.img(src='/images/logo_lofi.png',
                                   style='max-width:100px;margin-top: 10px;'))
                header.add(a_tag)
            else:
                header.add(tags.span(node.title, _class='navbar-brand'))

        bar = cont.add(tags.div(
            _class='navbar-collapse collapse',
            id=node_id,
        ))
        bar_list = bar.add(tags.ul(_class='nav navbar-nav'))

        for item in node.items:
            bar_list.add(self.visit(item))

        return root


flask_bootstrap.nav.BootstrapRenderer = BootstrapRendererNew


def make_nav(session):
    """ Creates the navigation using flask-nav.
    """
    pages = (session
             .query(Page)
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

    title = 'pygame'
    endpoint = 'news.index'
    # in tests, news.index might not exist. So we don't link there if not.
    try:
        url_for(endpoint)
        nav_bar = Navbar(View(title, endpoint))
    except (BuildError, RuntimeError):
        nav_bar = Navbar(title)

    nav_bar.items.extend(parts)
    return nav_bar


def add_nav(app):
    """ called by pygameweb.app.add_views_front
    """
    nav = Nav()

    @nav.navigation()
    def mynavbar():
        """ Every time a page is loaded we create the navigation.

        We cache the navbar in the templates.
        """
        return make_nav(current_session)

    nav.init_app(app)
