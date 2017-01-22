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


# def test_wiki_base(wiki_client):
#     """See if the wiki base path works.
#     """
#     resp = wiki_client.get('/wiki/')
#     assert resp.status_code == 200
#     assert b'Wiki' in resp.data

def test_wiki_index(wiki_client, session):
    """See if the wiki base path works.
    """
    from pygameweb.wiki.models import Wiki

    session.add(Wiki(link='index', title='Yo title', latest=1))
    session.commit()
    resp = wiki_client.get('/wiki/')
    assert resp.status_code == 200
    assert b'Yo title' in resp.data


def test_wiki_link(wiki_client, session):
    """See if the wiki base path works.
    """
    from pygameweb.wiki.models import Wiki
    wiki_page = Wiki(link='blabla', title='Yo title', latest=1)
    session.add(wiki_page)
    session.commit()

    # change the title.
    wiki_page.new_version(session)
    wiki_page.title = 'A new title for a new day'
    session.add(wiki_page)
    session.commit()

    resp = wiki_client.get('/wiki/blabla')
    assert resp.status_code == 200
    assert b'A new title for a new day' in resp.data
