"""What's new these days?
"""
import datetime
from email.utils import formatdate

from flask import Blueprint, render_template, request, make_response
from flask_sqlalchemy_session import current_session

from pygameweb.news.models import News
from pygameweb.cache import cache


news_blueprint = Blueprint('news',
                           __name__,
                           template_folder='../templates/')


def latest_news(session, per_page=10):
    return (session
            .query(News)
            .order_by(News.datetimeon.desc())
            .limit(per_page)
            .all())

@news_blueprint.route('/news.html', methods=['GET'])
@news_blueprint.route('/news', methods=['GET'])
@cache.cached(timeout=50)
def index():
    """ of the news page.
    """

    return render_template('news/view.html', news=latest_news(current_session))


@news_blueprint.route('/feed/atom', methods=['GET'])
def atom():
    """ of the news page.
    """
    resp = render_template('news/atom.xml', news=latest_news(current_session))
    response = make_response(resp)
    response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8; filename=news-ATOM'
    return response

    # This makes output which crashes a feed validator.
    # from werkzeug.contrib.atom import AtomFeed
    # news=latest_news(current_session)
    # feed = AtomFeed('pygame news', feed_url=request.url, url=request.url_root)
    # for new in news:
    #     feed.add(new.title, new.description_html,
    #              content_type='html',
    #              author='pygame',
    #              url='https://www.pygame.org/news.html',
    #              updated=new.datetimeon,
    #              published=new.datetimeon)
    # return feed.get_response()


@news_blueprint.route('/feed/rss', methods=['GET'])
def rss():
    """ of the news page.
    """
    build_date = formatdate(datetime.datetime.now().timestamp())
    resp = render_template('news/rss.xml', news=latest_news(current_session), build_date=build_date)

    response = make_response(resp)
    response.headers['Content-Type'] = 'application/xml; charset=ISO-8859-1; filename=news-RSS2.0'
    return response



# @news_blueprint.route('/feed/news.php?format=RSS2.0', methods=['GET'])
# @news_blueprint.route('/feed/news.php?format=ATOM', methods=['GET'])
@news_blueprint.route('/feed/news.php', methods=['GET'])
def legacy_feeds():
    feed_type = request.args.get('format', 'ATOM')
    if feed_type == 'ATOM':
        return atom()
    elif feed_type == 'RSS2.0':
        return rss()
    return ''


def add_news_blueprint(app):
    """ to the app.
    """
    app.register_blueprint(news_blueprint)
