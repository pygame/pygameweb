"""What's new these days?
"""
import datetime
from email.utils import formatdate

from flask import (
    Blueprint, render_template, request,
    make_response, redirect, url_for, abort
)
from flask_security import current_user, login_required, roles_required
from flask_sqlalchemy_session import current_session

from pygameweb.news.models import News, NewsAlert
from pygameweb.news.forms import NewsForm


news_blueprint = Blueprint(
    'news',
    __name__,
    template_folder='../templates/'
)


def news_for(slug, news_id=None):
    """ gets a News for the given 'slug'.
    """
    newsq = current_session.query(News)

    if slug is not None:
        newsq = newsq.filter(News.slug == slug)
    if news_id is not None:
        newsq = newsq.filter(News.id == news_id)

    news = newsq.first()
    if news is None:
        abort(404)

    return news

def news_alert_for(slug, news_alert_id=None):
    """ gets a NewsAlert for the given 'slug'.
    """
    newsq = current_session.query(NewsAlert)

    if slug is not None:
        newsq = newsq.filter(NewsAlert.slug == slug)
    if news_alert_id is not None:
        newsq = newsq.filter(NewsAlert.id == news_alert_id)

    news = newsq.first()
    if news is None:
        abort(404)

    return news


def latest_news(session, per_page=10):
    return (session
            .query(News)
            .order_by(News.datetimeon.desc())
            .limit(per_page)
            .all())

@news_blueprint.route('/news.html', methods=['GET'])
@news_blueprint.route('/news', methods=['GET'])
def index():
    """ of the news page.
    """
    return render_template(
        'news/view.html',
        news=latest_news(current_session)
    )


@news_blueprint.route('/', methods=['GET'])
def index_redirect():
    """ of the main url.
    """
    return redirect(url_for('news.index'))




@news_blueprint.route('/news/feed/atom', methods=['GET'])
def atom():
    """ of the news page.
    """
    resp = render_template(
        'news/atom.xml',
        news=latest_news(current_session)
    )
    response = make_response(resp)
    content_type = 'application/atom+xml; charset=utf-8; filename=news-ATOM'
    response.headers['Content-Type'] = content_type
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


@news_blueprint.route('/news/feed/rss', methods=['GET'])
def rss():
    """ of the news page.
    """
    build_date = formatdate(datetime.datetime.now().timestamp())
    resp = render_template(
        'news/rss.xml',
        news=latest_news(current_session),
        build_date=build_date
    )

    response = make_response(resp)
    content_type = 'application/xml; charset=ISO-8859-1; filename=news-RSS2.0'
    response.headers['Content-Type'] = content_type
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


@news_blueprint.route('/news/<path:slug>', methods=['GET'])
def view(slug):
    """
    """
    return render_template('news/viewone.html',
                           slug=slug,
                           news_id=None,
                           news_for=news_for)


@news_blueprint.route('/news-view/<int:news_id>', methods=['GET'])
def view_news_id(news_id):
    """
    """
    return render_template('news/viewone.html',
                           slug=None,
                           news_id=news_id,
                           news_for=news_for)


@news_blueprint.route('/news-alert-view/<int:news_alert_id>', methods=['GET'])
def view_news_alert_id(news_alert_id):
    """
    """
    return render_template('news/viewalert.html',
                           slug=None,
                           news_alert_id=news_alert_id,
                           news_alert_for=news_alert_for)


@news_blueprint.route('/news/<path:slug>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_news(slug):
    news = news_for(slug)

    if request.method == 'GET':
        form = NewsForm(obj=news)
    else:
        form = NewsForm()

    if form.validate_on_submit():
        news.title = form.title.data
        news.description = form.description.data
        news.summary = form.summary.data
        current_session.add(news)
        current_session.commit()
        return redirect(url_for('news.view', slug=news.slug))

    return render_template('news/editnews.html',
                           form=form,
                           slug=slug)


@news_blueprint.route('/news/new', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def new_news():
    """ posts a new piece of news.
    """
    form = NewsForm()
    if form.validate_on_submit():
        when = datetime.datetime.now()
        news = News(
            title=form.title.data,
            description=form.description.data,
            summary=form.summary.data,
            datetimeon=datetime.datetime.utcnow(),
            submit_users_id=current_user.id
        )
        current_session.add(news)
        current_session.commit()
        return redirect(url_for('news.view', slug=news.slug))

    return render_template('news/newnews.html', form=form)


def add_news_blueprint(app):
    """ to the app.
    """
    app.register_blueprint(news_blueprint)
