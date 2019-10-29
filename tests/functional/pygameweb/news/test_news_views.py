"""
"""

import pytest


@pytest.fixture
def news_client(app, session, client):
    """Fixture for wiki tests.
    """
    from pygameweb.news.views import add_news_blueprint
    from pygameweb.user.views import add_user_blueprint
    add_user_blueprint(app)
    add_news_blueprint(app)
    return client


@pytest.fixture
def news(session):
    from pygameweb.news.models import News
    import datetime
    new1 = News(
        title='title1',
        description='description',
        summary='short summary',
        datetimeon=datetime.datetime(2018, 3, 7, 10, 11)
    )
    new2 = News(
        title='title2',
        description='description2',
        summary='short summary2',
        datetimeon=datetime.datetime(2018, 3, 7, 10, 12)
    )
    session.add(new1)
    session.add(new2)
    session.commit()
    return [new1, new2]


@pytest.fixture
def news_alert(session):
    from pygameweb.news.models import NewsAlert
    import datetime
    new1 = NewsAlert(
        title='title1',
        description='description alert',
        summary='short summary',
        datetimeon=datetime.datetime(2018, 3, 7, 10, 11)
    )
    new2 = NewsAlert(
        title='title2',
        description='description2 alert',
        summary='short summary2',
        datetimeon=datetime.datetime(2018, 3, 7, 10, 12)
    )
    session.add(new1)
    session.add(new2)
    session.commit()
    return [new1, new2]

def test_news_model(news_client, session, news):
    assert news[0].slug == '2018/3/title1'
    assert news[1].slug == '2018/3/title2'

def test_news_view(news_client, session, news, news_alert):
    """ is shown as the default.
    """
    resp = news_client.get('/news')
    assert resp.status_code == 200
    assert news[0].title.encode('utf8') in resp.data
    assert news[0].description_html.encode('utf8') in resp.data
    assert news[1].title.encode('utf8') in resp.data
    assert news[1].description_html.encode('utf8') in resp.data

    assert news_client.get('/news.html').status_code == 200

    resp = news_client.get(f'/news-alert-view/{news_alert[0].id}')
    assert resp.status_code == 200
    assert news_alert[0].description_html.encode('utf8') in resp.data


@pytest.mark.parametrize("feed_url", [
    '/feed/news.php?format=ATOM',
    '/feed/news.php?format=RSS2.0',
    '/news/feed/rss',
    '/news/feed/atom'
])
def test_news_feeds(news_client, session, news, feed_url):
    """ have our news in them, and can be feedparsed.
    """
    import feedparser
    resp = news_client.get(feed_url)
    assert resp.status_code == 200
    assert news[0].title.encode('utf8') in resp.data
    assert news[0].description_html.encode('utf8') in resp.data
    assert news[1].title.encode('utf8') in resp.data
    assert news[1].description_html.encode('utf8') in resp.data

    parsed = feedparser.parse(resp.data)
    assert parsed['feed']['title'] == 'pygame news'
    assert parsed['entries'][0]['title'] == 'title2'
    assert parsed['entries'][0]['link'] == 'http://localhost/news/2018/3/title2'
    assert parsed['entries'][1]['title'] == 'title1'
    assert parsed['entries'][1]['link'] == 'http://localhost/news/2018/3/title1'



def test_news_slug(news_client, session, news):
    """ returns the right news for the given news id. But not all news.
    """

    url = f'/news/{news[0].slug}'
    resp = news_client.get(url)
    assert resp.status_code == 200
    assert news[0].title.encode('utf8') in resp.data
    assert news[1].title.encode('utf8') not in resp.data





def a_user(app, session, news_client, name, email,
           logged_in, disabled, active):
    """ gives us a user who is a member.
    """
    from pygameweb.user.models import User, Group
    from flask_security.utils import encrypt_password
    group = Group(name='admin', title='Admin')
    user = User(name=name,
                email=email,
                password=encrypt_password('password'),
                disabled=disabled,
                active=active,
                roles=[group])
    session.add(user)
    session.commit()

    # https://flask-login.readthedocs.org/en/latest/#fresh-logins
    with news_client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True
    return user


@pytest.fixture
def user(app, session, news_client):
    """ gives us a user who is a member.
    """
    return a_user(
        app,
        session,
        news_client,
        'joe',
        'asdf@example.com',
        logged_in=True,
        disabled=0,
        active=True
    )

def test_news_new(news_client, session, user):
    """ adds news.
    """
    from io import BytesIO
    from pygameweb.news.models import News

    resp = news_client.get('/news/new')
    assert resp.status_code == 200

    resp = news_client.post(
        '/news/new',
        data=dict(
            title='Title of news',
            summary='summary',
            description='description of project',
        ),
        follow_redirects=True
    )
    assert resp.status_code == 200
    news = (
        session
        .query(News)
        .filter(News.title == 'Title of news')
        .first()
    )
    assert news.title == 'Title of news'

    resp = news_client.get(f'/news/{news.slug}')
    assert resp.status_code == 200
    assert news.title.encode('utf8') in resp.data
