"""Adding static folders.
"""

from flask import Blueprint, send_from_directory#, render_template, abort, redirect, url_for, request, Response
from pathlib import Path

static_blueprint = Blueprint('static',
                             __name__,
                             template_folder='../templates/')


#files = ['lofi.html', 'hifi.html', 'server.json']
files = ['lofi.html', 'server.json']
folders = ['content', 'contests', 'css', 'ctypes', 'docs', 'docs-old', 'ftp', 'galleries',
           'gamelets', 'games', 'html5media', 'images', 'interview', 'iscroll', 'js',
           'ludumcontest1', 'ludumcontest2', 'mediaelement', 'mediagit', 'music', 'neu',
           'new', 'old', 'old_bug_attachments', 'oldhtml', 'pcr', 'pcr_old', 'pygame_wincvs',
           'search', 'shredwheat', 'siteswing', 'skins', 'swfs', 'test', 'thumb', 'tiny_mce',
           'tinymce_3_2_3_1', 'tmp', 'webalizer']



def add_folder(app, static_blueprint, folder):
    """Add a static folder.
    """
    def download_file(path):
        full_path = str(Path('..', app.config['WWW']) / folder)
        return send_from_directory(full_path, path)

    url = f'/{folder}/<path:path>'
    path = f'static_{folder}'
    app.add_url_rule(url, path, download_file)

def add_file(app, static_blueprint, file):

    def download_file():
        full_path = str(Path('..', app.config['WWW']))
        return send_from_directory(full_path, file)

    url = f'/{file}'
    path = f'static_{file}'
    app.add_url_rule(url, path, download_file)



def add_static_blueprint(app):
    """ to the app.
    """
    if 1 or app.config['DEBUG']:
        # Don't really need these files in production. A real webserver serves them.
        for folder in folders:
            add_folder(app, static_blueprint, folder)
        for file in files:
            add_file(app, static_blueprint, file)

        app.register_blueprint(static_blueprint)
