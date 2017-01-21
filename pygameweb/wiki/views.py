from flask import Blueprint, render_template, abort
# The sqlalchemy session is per request.
# http://flask-sqlalchemy-session.readthedocs.org/en/v1.1/
from flask_sqlalchemy_session import current_session
# from flask_admin import expose, AdminIndexView

wiki_blueprint = Blueprint('wiki',
                           __name__,
                           template_folder='../templates/')


@wiki_blueprint.route('/wiki/', methods=['GET'])
def wiki():
    """
    """
    return render_template('wiki.html')


def add_wiki_blueprint(app):
    """ to the app.
    """
    app.register_blueprint(wiki_blueprint)

