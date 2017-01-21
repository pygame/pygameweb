from flask import Blueprint, render_template, abort
# http://flask-sqlalchemy-session.readthedocs.org/en/v1.1/
from flask_sqlalchemy_session import current_session

from pygameweb.wiki.models import Wiki




wiki_blueprint = Blueprint('wiki',
                           __name__,
                           template_folder='../templates/')


@wiki_blueprint.route('/wiki/', methods=['GET'])
@wiki_blueprint.route('/wiki/<link>', methods=['GET'])
def index(link='index'):
    """
    """
    result = (current_session
              .query(Wiki)
              .filter(Wiki.link == link)
              .filter(Wiki.latest == 1)
              .first())

    if not result:
        abort(404)

    return render_template('wiki.html', wiki=result)


@wiki_blueprint.route('/wiki/<link>/edit', methods=['GET'])
def edit(link):
    """
    """
    result = (current_session
              .query(Wiki)
              .filter(Wiki.link == link)
              .filter(Wiki.latest == 1)
              .first())

    if not result:
        abort(404)

    return render_template('wiki_edit.html', wiki=result)


# @wiki_blueprint.route('/wiki/<link>/edit', methods=['POST'])
# def save(link):
#     """
#     """



def add_wiki_blueprint(app):
    """ to the app.
    """
    app.register_blueprint(wiki_blueprint)

