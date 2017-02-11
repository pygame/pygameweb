"""
"""

import pytest


@pytest.fixture
def news_client(app, session, client):
    """Fixture for wiki tests.
    """
    from pygameweb.news.views import add_news_blueprint
    add_news_blueprint(app)
    return client


@pytest.fixture
def news(session):
    from pygameweb.news.models import News
    import datetime
    now = datetime.datetime.now
    new1 = News(title='title1', description='description', datetimeon=now())
    new2 = News(title='title2', description='description2', datetimeon=now())
    session.add(new1)
    session.add(new2)
    session.commit()
    return [new1, new2]


def test_news_view(news_client, session, news):
    """ is shown as the default.
    """
    resp = news_client.get('/news')
    assert resp.status_code == 200
    assert news[0].title.encode('utf8') in resp.data
    assert news[0].description_html.encode('utf8') in resp.data
    assert news[1].title.encode('utf8') in resp.data
    assert news[1].description_html.encode('utf8') in resp.data

    assert news_client.get('/news.html').status_code == 200


@pytest.mark.parametrize("feed_url", [
    '/feed/news.php?format=ATOM',
    '/feed/news.php?format=RSS2.0',
    '/feed/rss',
    '/feed/atom'
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
    assert parsed['entries'][1]['title'] == 'title1'
