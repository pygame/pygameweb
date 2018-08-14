""" Herein we test if all the different wiki interactions work.
"""

import pytest


@pytest.fixture
def wiki_client(app, session, client):
    """Fixture for wiki tests.
    """
    from pygameweb.wiki.views import add_wiki_blueprint
    from pygameweb.user.views import add_user_blueprint
    add_user_blueprint(app)
    add_wiki_blueprint(app)
    return client


@pytest.fixture
def user(app, session, wiki_client):
    """ gives us a user who is a member.
    """
    from pygameweb.user.models import User
    from flask_security.utils import encrypt_password
    user = User(name='joe',
                email='asdf@example.com',
                password=encrypt_password('password'))
    session.add(user)
    session.commit()
    # https://flask-login.readthedocs.org/en/latest/#fresh-logins
    with wiki_client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True

    return user


@pytest.fixture
def member(session, user):
    """
    """
    from pygameweb.user.models import Group
    group = Group(name='members', title='Member')
    user.roles.append(group)
    session.add(group)
    session.commit()
    return group


@pytest.fixture
def admin(session, user):
    """
    """
    from pygameweb.user.models import Group
    group = Group(name='admin', title='Admin')
    user.roles.append(group)
    session.add(group)
    group = Group(name='members', title='Member')
    user.roles.append(group)
    session.add(group)
    session.commit()
    return group


@pytest.fixture
def wiki_page_info(session):
    import datetime
    from pygameweb.wiki.models import Wiki

    first_content = 'some content<br/> yo.'
    second_content = 'We all love content.'
    first_changes = 'first wiki page version is done'
    second_changes = 'new changes to the wiki page'

    wiki_page = Wiki(link='blablabla',
                     title='Yo title',
                     datetimeon=datetime.datetime(2017, 1, 12),
                     content=first_content,
                     changes=first_changes,
                     latest=1)
    session.add(wiki_page)
    session.commit()

    first_id = wiki_page.id

    # change the title.
    wiki_page.new_version(session)
    wiki_page.title = 'A new title for a new day'
    wiki_page.content = second_content
    wiki_page.changes = second_changes

    session.add(wiki_page)
    session.commit()

    return [wiki_page, first_content, second_content,
            first_id, first_changes, second_changes]


def test_wiki_link(wiki_client, session, wiki_page_info):
    """ works when we pass the correct wiki link.
    """
    wiki_page, first_content, second_content, first_id, _, _ = wiki_page_info

    second_id = wiki_page.id
    assert second_id != first_id

    for link in ['/wiki/blablabla', '/wiki/blablabla/']:
        resp = wiki_client.get(link)
        assert resp.status_code == 200
        assert b'A new title for a new day' in resp.data

    resp = wiki_client.get('/wiki/blablabla?action=source')
    assert resp.status_code == 200
    expected = b'A new title for a new day'
    assert expected not in resp.data, 'because only the content is shown'
    assert second_content in resp.data.decode('utf-8')

    resp = wiki_client.get(f'/wiki/blablabla?action=source&id={first_id}')
    assert (first_content in
            resp.data.decode('utf-8')), 'because old page version still there'

    url = ('/wiki/blablabla?action=diff&oldid={oldid}&newid={newid}'
           .format(oldid=first_id, newid=second_id))
    resp = wiki_client.get(url)
    assert b'<div class="delete">-' in resp.data, 'some lines are deleted'
    assert b'<div class="insert">+' in resp.data, 'some lines are inserted'

    resp = wiki_client.get('/wiki/blablabla?action=history')
    assert resp.status_code == 302, 'login member required'


def test_wiki_recent(wiki_client, session, wiki_page_info):
    """ works when we pass the correct wiki link.
    """
    (_, _, _, _, first_changes, second_changes) = wiki_page_info
    resp = wiki_client.get('/wiki/recent')
    assert resp.status_code == 200
    resp = wiki_client.get('/wiki/recent.php')
    assert resp.status_code == 200
    assert first_changes in resp.data.decode('utf-8')
    assert second_changes in resp.data.decode('utf-8')


def test_wiki_link_login(wiki_client, session, wiki_page_info, member):

    resp = wiki_client.get('/wiki/blablabla?action=history')
    assert resp.status_code == 200
    assert b'new changes to the wiki page' in resp.data
    assert b'first wiki page version is done' in resp.data


def test_wiki_locked(wiki_client, session, wiki_page_info, user):
    """ stops a page from being edited or reverted.
    """
    wiki_page, first_content, second_content, first_id, _, _ = wiki_page_info
    wiki_page.locked = True
    session.add(wiki_page)
    session.commit()

    resp = wiki_client.get('/wiki/blablabla/edit')
    assert resp.status_code == 302
    assert resp.location == 'http://localhost/'

    data = dict(changes='I have changed.', content='some content')
    resp = wiki_client.post('/wiki/blabla/edit',
                            data=data)
    assert resp.status_code == 302
    assert resp.location == 'http://localhost/'


def test_wiki_locked_admin(wiki_client, session, wiki_page_info, user, admin):
    """ admin should be able to edit it, and revert it.
    """
    wiki_page, first_content, second_content, first_id, _, _ = wiki_page_info
    wiki_page.locked = True
    session.add(wiki_page)
    session.commit()

    resp = wiki_client.get('/wiki/blablabla/edit')
    assert resp.status_code == 200

    data = dict(changes='I have changed.', content='some content')
    resp = wiki_client.post('/wiki/blabla/edit',
                            data=data)
    assert resp.status_code == 302
    assert resp.location == 'http://localhost/wiki/blabla'


def test_wiki_new_page(wiki_client, session, member, user):
    """ is editable when we go there.
    """
    from pygameweb.wiki.models import Wiki

    resp = wiki_client.get('/wiki/blabla')
    assert resp.status_code == 404, 'now there is no blabla page.'

    resp = wiki_client.get('/wiki/blabla/edit')
    assert resp.status_code == 200
    assert b'blabla' in resp.data

    data = dict(changes='I have changed.', content='some content')
    resp = wiki_client.post('/wiki/blabla/edit',
                            data=data,
                            follow_redirects=True)

    assert resp.status_code == 200
    assert b'blabla' in resp.data
    assert b'some content' in resp.data

    wik = session.query(Wiki).filter(Wiki.users_id == user.id).first()
    assert wik.content == data['content'], 'user id added to this version'

    resp = wiki_client.get('/wiki/blabla')
    assert resp.status_code == 200
    assert b'blabla' in resp.data
    assert b'some content' in resp.data, 'now the blabla page exists'

    resp = wiki_client.get('/wiki/blabla?action=history')
    assert resp.status_code == 200
    assert b'I have changed.' in resp.data


def test_wiki_index(wiki_client, session):
    """ is shown as the default.
    """
    from pygameweb.wiki.models import Wiki

    session.add(Wiki(link='index', title='Yo title', latest=1))
    session.commit()
    resp = wiki_client.get('/wiki/')
    assert resp.status_code == 200
    assert b'Yo title' in resp.data
