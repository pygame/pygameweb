""" Load comments from xml into the db.
"""

import pytest


@pytest.fixture
def comment_client(app, session, client):
    """Fixture for wiki tests.
    """
    from pygameweb.comment.views import add_comment
    from pygameweb.user.views import add_user_blueprint
    add_user_blueprint(app)
    add_comment(app)
    return client


@pytest.fixture
def user(app, session, comment_client):
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
    with comment_client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True

    return user


@pytest.fixture
def moderator(session, user):
    """
    """
    from pygameweb.user.models import Group
    group = Group(name='moderator', title='Moderator')
    user.roles.append(group)
    session.add(group)
    session.commit()
    return group


xml_example = """<?xml version="1.0" encoding="utf-8"?>
<disqus xmlns:dsq="http://disqus.com/disqus-internals"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://disqus.com/api/schemas/1.0/disqus.xsd
        http://disqus.com/api/schemas/1.0/disqus-internals.xsd">
  <category dsq:id="796386">
    <forum>someforum</forum>
    <title>General</title>
    <isDefault>true</isDefault>
  </category>
  <thread dsq:id="291435028">
    <id/>
    <forum>someforum</forum>
    <category dsq:id="796386"/>
    <link>http://example.com/project//</link>
    <title>http://example.com/project//</title>
    <message/>
    <createdAt>2011-04-29T16:46:28Z</createdAt>
    <author>
      <email>r@example.com</email>
      <name>Some r name</name>
      <isAnonymous>true</isAnonymous>
    </author>
    <ipAddress>1.1.1.1</ipAddress>
    <isClosed>false</isClosed>
    <isDeleted>false</isDeleted>
  </thread>
  <thread dsq:id="291436016">
    <id>some_project_1310</id>
    <forum>someforum</forum>
    <category dsq:id="796386"/>
    <link>http://example.com/project/1310/</link>
    <title>pygame - python game development</title>
    <message/>
    <createdAt>2011-04-29T16:47:54Z</createdAt>
    <author>
      <email>r@example.com</email>
      <name>Some r name</name>
      <isAnonymous>true</isAnonymous>
    </author>
    <ipAddress>1.1.1.1</ipAddress>
    <isClosed>false</isClosed>
    <isDeleted>false</isDeleted>
  </thread>
  <thread dsq:id="291436086">
    <id>some_project_1820</id>
    <forum>someforum</forum>
    <category dsq:id="796386"/>
    <link>http://example.com/project/1820/</link>
    <title>Some title</title>
    <message/>
    <createdAt>2011-04-29T16:48:00Z</createdAt>
    <author>
      <email>r@example.com</email>
      <name>Some r name</name>
      <isAnonymous>true</isAnonymous>
    </author>
    <ipAddress>1.1.1.1</ipAddress>
    <isClosed>false</isClosed>
    <isDeleted>false</isDeleted>
  </thread>
  <post dsq:id="194227070">
    <id/>
    <message>&lt;p&gt;Another message is here..&lt;/p&gt;</message>
    <createdAt>2011-04-29T16:57:46Z</createdAt>
    <isDeleted>false</isDeleted>
    <isSpam>false</isSpam>
    <author>
      <email>r@example.com</email>
      <name>Some r name</name>
      <isAnonymous>true</isAnonymous>
    </author>
    <ipAddress>1.1.1.1</ipAddress>
    <thread dsq:id="291436086"/>
  </post>
  <post dsq:id="194229307">
    <id/>
    <message>&lt;p&gt;Another message.&lt;/p&gt;</message>
    <createdAt>2011-04-29T17:00:07Z</createdAt>
    <isDeleted>false</isDeleted>
    <isSpam>false</isSpam>
    <author>
      <email>r@example.com</email>
      <name>Some r name</name>
      <isAnonymous>true</isAnonymous>
    </author>
    <ipAddress>1.1.1.1</ipAddress>
    <thread dsq:id="291436086"/>
  </post>
  <post dsq:id="194253320">
    <id/>
    <message>&lt;p&gt;Some message ok.&lt;/p&gt;</message>
    <createdAt>2011-04-29T17:39:31Z</createdAt>
    <isDeleted>false</isDeleted>
    <isSpam>false</isSpam>
    <author>
      <email>a@example.com</email>
      <name>Some name a</name>
      <isAnonymous>false</isAnonymous>
      <username>blablax</username>
    </author>
    <ipAddress>2.2.2.2</ipAddress>
    <thread dsq:id="291436086"/>
    <parent dsq:id="194229307"/>
  </post>
  <post dsq:id="194253444">
    <id/>
    <message>&lt;p&gt;Some X message ok.&lt;/p&gt;</message>
    <createdAt>2011-04-29T17:39:31Z</createdAt>
    <isDeleted>false</isDeleted>
    <isSpam>false</isSpam>
    <author>
      <email>a@example.com</email>
      <name>Some name a</name>
      <isAnonymous>false</isAnonymous>
      <username>blablax</username>
    </author>
    <ipAddress>2.2.2.2</ipAddress>
    <thread dsq:id="291436086"/>
    <parent dsq:id="194253320"/>
  </post>
</disqus>"""


def test_comment_load(session):
    """
    """
    from pygameweb.comment.models import load_xml, CommentPost
    from io import BytesIO

    # load_xml(session, 'comments.xml')
    load_xml(session, BytesIO(xml_example.encode('utf8')))

    post = (session
            .query(CommentPost)
            .filter(CommentPost.id == 194253320)
            .first())
    assert post.parent.id == 194229307
    post2 = (session
             .query(CommentPost)
             .filter(CommentPost.id == 194229307)
             .first())
    assert post2.children[0].id == 194253320
    assert post.thread.id == 291436086
    assert post2.thread.id == 291436086

    post3 = (session
             .query(CommentPost)
             .filter(CommentPost.id == 194227070)
             .first())
    assert post3.thread.id == 291436086
    assert len(post3.children) == 0
    assert post3.parent is None

    # get all the top level posts for a thread_id
    thread_id = 291436086
    posts = CommentPost.in_thread(session, thread_id)

    num_top_level_posts = 2
    assert (len(posts)) == num_top_level_posts
    first_post_id = 194227070
    assert posts[0].id == first_post_id
    assert posts[1].children[0].children[0].id == 194253444

    forum = 'someforum'
    id_text = 'some_project_1820'
    posts = CommentPost.for_thread(session, forum, id_text)
    assert (len(posts)) == num_top_level_posts
    assert posts[0].id == first_post_id
    assert posts[1].children[0].children[0].id == 194253444

    assert posts[0].thread.link == 'http://example.com/project/1820/'
    assert posts[0].thread.link_path == '/project/1820/', 'just the path'


def test_recent_comments(session, comment_client):
    """ are being rendered.
    """

    from pygameweb.comment.models import load_xml
    from io import BytesIO

    # load_xml(session, 'comments.xml')
    load_xml(session, BytesIO(xml_example.encode('utf8')))

    resp = comment_client.get('/comments/pygame')
    assert resp.status_code == 200


def test_comments_jquery_there(comment_client):
    """ as it is used by the documentation.
    """
    resp = comment_client.get('/comments/jquery.plugin.docscomments.js')
    assert resp.status_code == 200
