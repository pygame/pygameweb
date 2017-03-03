"""For creating thumbnails.
"""

from flask import Blueprint#, render_template, abort, redirect, url_for, request, Response



thumb_blueprint = Blueprint('thumb',
                            __name__,
                            template_folder='../templates/')




def add_thumb_blueprint(app):
    """ to the app.
    """
    from pygameweb.cache import limiter
    limiter.limit("1000/hour")(thumb_blueprint)

    app.register_blueprint(thumb_blueprint)
