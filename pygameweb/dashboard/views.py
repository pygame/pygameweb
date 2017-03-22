"""The dashboard shows a collection of pygame modules.
"""

from pathlib import Path

from flask import (Blueprint, render_template, abort, current_app,
                   send_from_directory, request)
from pygameweb.thumb import image_thumb

dashboard_blueprint = Blueprint('dashboard',
                                __name__,
                                template_folder='../templates/')


# @dashboard_blueprint.route('/hifi.html', methods=['GET'])
@dashboard_blueprint.route('/dashboard-dev', methods=['GET'])
def index():
    """ This either shows a page if it exists, or does a redirect.
    """
    is_crawler = 'our-web-crawler' in request.headers.get('User-Agent', '')
    return render_template('dashboard/index.html', is_crawler=is_crawler)


@dashboard_blueprint.route('/hifi.html', methods=['GET'])
@dashboard_blueprint.route('/dashboard', methods=['GET'])
def dashboard():
    """ we send the www/dashboard-dev file made with generate_static.
    """
    full_path = Path(current_app.config['WWW'])
    full_path_str = str(full_path.absolute())
    return send_from_directory(full_path_str,
                               'dashboard-dev',
                               mimetype='text/html')


@dashboard_blueprint.route('/screens-300/<path:fname>', methods=['GET'])
@dashboard_blueprint.route('/screenshots-300/<path:fname>', methods=['GET'])
def screenshots300(fname):
    """ Return an 300px wide screenshot image.
    """
    full_path = Path(current_app.config['WWW'])
    img_fname = image_thumb(full_path, fname, 300, 200)
    if img_fname is None:
        abort(404)
    return send_from_directory(full_path.absolute(), img_fname.lstrip('/'))


def add_dashboard(app):
    """
    """
    app.register_blueprint(dashboard_blueprint)
