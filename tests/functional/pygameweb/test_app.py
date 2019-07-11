

def test_create_app(app):
    """ can we create an app?
    """
    assert app
    assert app.engine

def test_custom_error_page_404(client):
    """ is shown when a route does not exist.
    """
    resp = wiki_client.get('/thisshouldnotexist')
    assert resp.status_code == 404
    assert b'<a href="/">Home</a>' in resp.data

@pytest.fixture
def error_client(app, client):
    """Add a route which raises 500 error.
    """
    @app.route('/this500s')
    def error_on_purpose():
        raise Exception('oops')
    return client

def test_custom_error_page_500(client):
    """ is shown on a 500 error"""
    resp = wiki_client.get('/this500s')
    assert resp.status_code == 500
    assert b'<a href="/">Home</a>' in resp.text
    #from pyquery import PyQuery as pq
    #assert pq(resp.text).find('a:contains(Home)').length
