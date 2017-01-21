"""For running the app(s) locally. For uwsgi see pygameweb.app_front etc.

    # http://flask.pocoo.org/docs/0.12/patterns/appdispatch/

"""

import click
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from pygameweb.app import create_app, add_views_front


def run_app(add_view_funcs=None, url_prefix='', port=None):
    """

    :param url_prefix: where to host under. For example /webapp
    :param port: to run on.
    """

    app = create_app('pygameweb.config.Config')
    if add_view_funcs is not None:
        for add_views in add_view_funcs:
            add_views(app)

    def empty_app(_, resp):
        """Empty app, to make DispatcherMiddeware happy if we use prefix == ''.
        """
        resp(b'200 OK', [(b'Content-Type', b'text/plain')])
        return [b'']

    app.config['APPLICATION_ROOT'] = url_prefix
    run_simple(app.config['HOST'],
               int(app.config['PORT']) if port is None else int(port),
               DispatcherMiddleware(empty_app, {url_prefix: app}),
               use_reloader=app.config['DEBUG'],
               use_debugger=app.config['DEBUG'])


@click.command()
@click.option('--port', default=None, help='Network port.')
@click.option('--url_prefix', default='', help='')
def run_front(url_prefix='', port=None):
    """ Run the front end one.
    """
    run_app([add_views_front], url_prefix, port)
