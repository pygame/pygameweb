""" Do the pages and navigation system work? Probably.
"""

import pytest


@pytest.fixture
def page_client(app, session, client):
    """Fixture for wiki tests.
    """
    from pygameweb.page.views import add_page
    from pygameweb.nav.views import add_nav
    add_page(app)
    add_nav(app)

    return client


@pytest.fixture
def pages(session):
    """
    """
    from pygameweb.page.models import Page

    page1 = Page(name='pagename1',
                 title='pagetitle1',
                 content='Some great content.',
                 orders=1,
                 link='content.html',
                 hidden=0)

    page2 = Page(name='Download Redirect',
                 orders=2,
                 link='redirect.html',
                 hidden=0,
                 uri='/redirected_to.html')

    page3 = Page(name='Hidden page',
                 title='pagetitle1',
                 content='hidden content',
                 orders=3,
                 link='hidden.html',
                 hidden=1)

    page4 = Page(name='Page Group1',
                 content='Second best content.',
                 orders=4,
                 link='group1.html',
                 hidden=0,
                 nav_group='Can We Be')

    page5 = Page(name='Page Group2',
                 content='More Second best content.',
                 orders=5,
                 link='group2.html',
                 hidden=0,
                 nav_group='Can We Be')

    # don't show this in the navigation.
    page6 = Page(name='Download Redirect Hidden',
                 orders=2,
                 link='hidden-redirect.html',
                 hidden=1,
                 uri='/hidden-redirected_to.html')

    the_pages = [page1, page2, page3, page4, page5, page6]
    for page in the_pages:
        session.add(page)
    session.commit()
    return the_pages


def test_page(page_client, session, pages):
    """
    """
    resp = page_client.get('content.html')
    assert resp.status_code == 200
    assert b'Some great content.' in resp.data, 'content page'

    resp = page_client.get('hidden.shtml')
    assert resp.status_code == 404, 'hidden pages'

    resp = page_client.get('redirect.html')
    assert resp.status_code == 302
    assert 'redirected_to.html' in resp.location, 'redirects'

    resp = page_client.get('hidden-redirect.html')
    assert resp.status_code == 302
    assert 'hidden-redirected_to.html' in resp.location, (
           'because redirects when it is hidden from navigation')


def test_nav(pages, session):
    """ is there.
    """
    from pygameweb.nav.views import make_nav
    nav = make_nav(session)
    assert nav.items[0].text == 'pagename1'
    assert nav.items[1].text == 'Download Redirect'

    assert nav.items[2].title == 'Can We Be', 'subgroup'
    assert nav.items[2].items[0].text == 'Page Group1'
    assert nav.items[2].items[1].text == 'Page Group2'
