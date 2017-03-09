"""bitbucket.org related things.
"""
from subprocess import run
import os

bitbucket_url = os.environ.get('APP_BITBUCKET_URL', '/bitbucket')



def add_builds(app):
    """ to the app.
    """
    @app.route(bitbucket_url, methods=['POST', 'GET'])
    def bitbucket(**kwargs):
        run(['pygameweb_update_docs'])
        run(['pygameweb_launchpad'])
        return 'sweet'
