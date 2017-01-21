import pytest



@pytest.fixture
def wiki_client(app, client):
    """Fixture for wiki tests.
    """
    from pygameweb.wiki.views import add_wiki_blueprint
    from flask_bootstrap import Bootstrap
    Bootstrap(app)

    add_wiki_blueprint(app)
    return client


def test_wiki_base(wiki_client):
    """See if the wiki base path works.
    """
    resp = wiki_client.get('/wiki/')
    assert resp.status_code == 200
    assert b'Wiki' in resp.data
