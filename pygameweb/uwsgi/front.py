""" Run the front end app. This is mainly for uwsgi.
"""

# http://flask.pocoo.org/docs/0.12/deploying/uwsgi/
# uwsgi -s /tmp/uwsgi.sock -w pygameweb.uwsgi.front:app
from pygameweb.app import create_app, add_views_front

from pygameweb.config import Config
config = Config()
app = create_app('pygameweb.config.Config')
add_views_front(app)
