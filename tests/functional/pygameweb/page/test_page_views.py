"""
"""

import pytest
import mock


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
    import datetime
    from pygameweb.page.models import Page


    page1 = Page(name='pagename1',
                 title='pagetitle1',
                 keywords='',
                 content='',
                 summary='',
                 orders=1,
                 link='',
                 hidden=0,
                 uri='',
                 users_id=1,
                 groups_id=1,
                 nav_group='')

    session.add(page1)

    return [page1]



def test_page(page_client, session, pages):
    """
    """
    from pygameweb.page.models import Page


    # projects = (session
    #             .query(Project)
    #             .filter(Tags.project_id == Project.id)
    #             .filter(Tags.value == 'arcade')
    #             .offset(start)
    #             .limit(per_page)
    #             .all())

    # resp = project_client.get('/tags/game')
    # assert resp.status_code == 200

    assert 'content pages'
    assert 'redirects'
    assert 'hidden pages'


def test_nav():
    """ is there.
    """

def test_nav_groups():
    """ show nav items in correct groups.
    """

def test_nav_order():
    """ is respected.
    """

