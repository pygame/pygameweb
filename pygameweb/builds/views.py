"""Building pygame, and doing stuff when things are merged.

github.com related webhook integration.
"""
import os
import json
from subprocess import run
import hmac
import hashlib
from flask import request, abort


github_url = os.environ.get('APP_GITHUB_WEBHOOK_URL', '/github')
github_secret = bytes(os.environ.get('APP_GITHUB_WEBHOOK_SECRET', ''), 'utf8')

def verify_github(secret, body, x_hub_signature):
    """ https://developer.github.com/webhooks/securing/
    """
    signature = 'sha1=' + hmac.new(secret, body, hashlib.sha1).hexdigest()
    return signature == x_hub_signature

def add_builds(app):
    """ to the app.
    """

    @app.route(github_url, methods=['POST', 'GET'])
    def github_webhook(**kwargs):
        """Called by github when something happens.

        When something goes on master branch, we:
          - build the documentation,
          - update the launchpad badge.

        https://developer.github.com/webhooks/
        """
        if not verify_github(github_secret,
                             request.get_data(),
                             request.headers.get('X-Hub-Signature', '')):
            abort(404)

        payload = request.form.get('payload', None)
        if payload:
            data = json.loads(payload)
            if hasattr(data, 'get'):
                if data.get('ref', None) == 'refs/heads/master':
                    run(['pygameweb_update_docs'])
                    run(['pygameweb_launchpad'])
        return 'sweet'
