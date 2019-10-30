from flask import render_template


def create_app(object_name='pygameweb.config.Config',
               engine=None,
               session_factory=None):
    """returns a flask app.

    http://flask.pocoo.org/docs/patterns/appfactories/

    :param object_name: the object to load the config from.
    :param engine: an sqlalchemy engine.
    :param session_factory: an sqlalchemy session_factory.
    """

    from flask import Flask
    from flask_bootstrap import Bootstrap
    from flask_mail import Mail

    from pygameweb import db
    app = Flask(__name__)
    app.config.from_object(object_name)
    Bootstrap(app)

    db.init(app, engine, session_factory)
    Mail(app)

    # https://flask-debugtoolbar.readthedocs.io/en/latest/
    if app.config['DEBUG'] and not app.config['TESTING']:
        app.config['DEBUG_TB_PROFILER_ENABLED'] = True
        app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

        from flask_debugtoolbar import DebugToolbarExtension
        try:
            # relies on a patched debugtoolbar
            DebugToolbarExtension(app, sqlalchemy_engine=app.engine)
        except TypeError:
            DebugToolbarExtension(app)

    from pygameweb.cache import cache, limiter
    cache.init_app(app)

    if not app.config['TESTING']:
        limiter.init_app(app)

    return app

def upgrade_https_urls(app):

    # use https with url_for when not in debug mode.
    use_https_urls = not app.config['DEBUG']
    if use_https_urls:
        class ForceHttpsUrlFor(object):
            def __init__(self, app):
                self.app = app
            def __call__(self, environ, start_response):
                environ['wsgi.url_scheme'] = 'https'
                return self.app(environ, start_response)
        app.wsgi_app = ForceHttpsUrlFor(app.wsgi_app)

    # make sure https://www. is used for login/logout/register links.
    from flask_security.utils import url_for_security
    def _url_for_security(endpoint, **values):
        return (url_for_security(endpoint, **values)
                .replace('https://pygame.org', 'https://www.pygame.org'))

    @app.context_processor
    def inject_url_for_image():
        return {'url_for_security': _url_for_security}


def http_error_handler(error):
    message = error.description
    if '  ' in message:
        message, sub = message.split('  ', 1)
    else:
        sub = ''
    return render_template('error.html', code=error.code, message=message, sub=sub), error.code


def error_handler(_):
    message = 'Internal Server Error'
    return render_template('error.html', code=500, message=message, sub=''), 500


def add_views_front(app):
    """ Adds all the front end views to the app.

    Kept separate from create_app so we can test individual views.
    """
    # We catch HTTPException to handle all HTTP error codes
    from werkzeug.exceptions import HTTPException

    # add_user_blueprint does some monkey patching, so it needs to be first.
    from pygameweb.user.views import add_user_blueprint
    add_user_blueprint(app)
    upgrade_https_urls(app)

    from pygameweb.wiki.views import add_wiki_blueprint
    from pygameweb.project.views import add_project_blueprint
    from pygameweb.static.views import add_static_blueprint
    from pygameweb.thumb.views import add_thumb_blueprint
    from pygameweb.news.views import add_news_blueprint
    from pygameweb.nav.views import add_nav
    from pygameweb.page.views import add_page
    from pygameweb.sidebar.views import add_sidebar
    from pygameweb.dashboard.views import add_dashboard
    from pygameweb.builds.views import add_builds
    from pygameweb.comment.views import add_comment

    # app.errorhandler(HTTPException)(http_error_handler)
    # app.errorhandler(Exception)(error_handler)

    add_wiki_blueprint(app)
    add_project_blueprint(app)
    add_thumb_blueprint(app)
    add_static_blueprint(app)
    add_news_blueprint(app)
    add_dashboard(app)
    add_page(app)
    add_sidebar(app)
    add_builds(app)
    add_comment(app)

    # nav should be last, since it uses other routes.
    add_nav(app)
    if app.config['ADMIN']:
        from pygameweb.admin.views import add_admin
        add_admin(app)
