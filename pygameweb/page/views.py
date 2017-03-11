"""

- find navigation links
    select name, uri, link, hidden, orders from node where link != '' AND hidden=0 order by orders;
- add page redirects
    - select name, uri, link, hidden, orders from node where link != '' AND hidden=1;
- add page views
    select name, uri, link, hidden, orders from node where link != '' AND hidden=0 order by orders;
    uri -> page(id)

"""



from flask import Blueprint, render_template, abort, redirect, url_for, request, Response, current_app
from flask_sqlalchemy_session import current_session

from pygameweb.user.models import User
from pygameweb.project.models import Project, Release, Tags, top_tags
from pygameweb.page.models import Page


page_blueprint = Blueprint('page',
                           __name__,
                           template_folder='../templates/')




def render_page(page):
    if page.id == 16:
        return render_template('page/screenshots.html', page=page)
    else:
        return render_template('page/view.html', page=page)


@page_blueprint.route('/<path:link>', methods=['GET'])
def page_link(link):
    """ This either shows a page if it exists, or does a redirect.
    """
    page = (current_session
            .query(Page)
            .filter(Page.link == link)
            .first()
           )

    if page is None:
        abort(404)

    if page.uri:
        return redirect(page.uri)

    return render_page(page)


def add_page(app):
    """
    """
    app.register_blueprint(page_blueprint)
