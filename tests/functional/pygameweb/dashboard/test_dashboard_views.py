"""
"""

import pytest

@pytest.fixture
def dashboard_client(app, session, client):
    """Fixture for wiki tests.
    """
    from pygameweb.dashboard.views import add_dashboard
    add_dashboard(app)
    return client



def test_dashboard_view(dashboard_client, session):
    """ is shown as the default.
    """
    resp = dashboard_client.get('/dashboard-dev')
    assert resp.status_code == 200

    # resp = dashboard_client.get('/screenshot-300/1.jpg')
    # assert resp.status_code == 200

    # resp = dashboard_client.get('/screens-300/1.jpg')
    # assert resp.status_code == 200
