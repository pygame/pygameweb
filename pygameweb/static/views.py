"""Adding static folders.

This serves up a whole bunch of static files and folders.
"""

from flask import Blueprint, send_from_directory
from pathlib import Path

static_blueprint = Blueprint('static',
                             __name__,
                             template_folder='../templates/')


files = ['lofi.html', 'server.json', 'hifi.html', 'favicon.ico', 'robots.txt']
folders = ['content', 'contests', 'css', 'ctypes', 'docs', 'docs-old', 'ftp',
           'galleries', 'gamelets', 'games', 'html5media', 'images',
           'interview', 'iscroll', 'js', 'ludumcontest1', 'ludumcontest2',
           'mediaelement', 'mediagit', 'music', 'neu', 'new', 'old',
           'old_bug_attachments', 'oldhtml', 'pcr', 'pcr_old', 'pygame_wincvs',
           'search', 'shots', 'shredwheat', 'siteswing', 'skins', 'swfs', 'test',
           'thumb', 'tiny_mce', 'tinymce_3_2_3_1', 'tmp', 'webalizer']


def is_there(app, full_path, file_folder):
    full_path = Path('..', app.config['WWW']) / file_folder
    return full_path.exists()


def add_folder(app, static_blueprint, folder):
    """Add a static folder.
    """
    full_path = Path(app.config['WWW']) / folder
    full_path_index = Path(app.config['WWW']) / folder / 'index.html'
    full_path_str = str(full_path.absolute())
    if not full_path.exists():
        return

    def download_file(path):
        return send_from_directory(full_path_str, path)

    url = f'/{folder}/<path:path>'
    path = f'static_{folder}'
    app.add_url_rule(url, path, download_file)

    if full_path_index.exists():
        def download_index_file():
            return send_from_directory(full_path_str, 'index.html')

        url = f'/{folder}/'
        path = f'static_{folder}_index'
        app.add_url_rule(url, path, download_index_file)


def add_file(app, static_blueprint, file):
    """Add a file to serve.
    """
    full_path = Path(app.config['WWW'])
    full_path_str = str(full_path.absolute())
    if not (full_path / file).exists():
        return

    def download_file():
        return send_from_directory(full_path_str, file)

    url = f'/{file}'
    path = f'static_{file}'
    app.add_url_rule(url, path, download_file)


def add_static_blueprint(app):
    """ to the app.
    """
    for folder in folders:
        add_folder(app, static_blueprint, folder)
    for file in files:
        add_file(app, static_blueprint, file)


    from pygameweb.cache import limiter
    limiter.limit("1000/hour")(static_blueprint)

    app.register_blueprint(static_blueprint)
