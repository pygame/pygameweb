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


def test_dashboard_view(app, dashboard_client, session, tmpdir):
    """ is shown as the default.
    """
    resp = dashboard_client.get('/dashboard-dev')
    assert resp.status_code == 200

    p = tmpdir.mkdir('tmpwww').join("dashboard-dev")
    p.write("content")

    app.config['WWW'] = str(p / '..')
    resp = dashboard_client.get('/dashboard')
    assert resp.status_code == 200
    assert b'content' in resp.data

    (p / '..' / 'thumb').mkdir()
    image = (p / '..' / 'shots').mkdir().join('1.png')

    png = (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
           b'\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT'
           b'\x08\x99c```\x00\x00\x00\x04\x00\x01\xa3\n\x15\xe3\x00\x00'
           b'\x00\x00IEND\xaeB`\x82')

    image.write_binary(png)

    resp = dashboard_client.get('/screenshots-300/1.png')
    assert resp.status_code == 200

    resp = dashboard_client.get('/screenshots-300/2.png')
    assert resp.status_code == 404

    # resp = dashboard_client.get('/screens-300/1.jpg')
    # assert resp.status_code == 200
