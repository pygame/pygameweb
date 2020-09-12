from pathlib import Path

import pytest
import mock


@pytest.fixture
def project_client(app, session, client):
    """Fixture for wiki tests.
    """
    from pygameweb.project.views import add_project_blueprint
    from pygameweb.user.views import add_user_blueprint
    from pygameweb.sidebar.views import add_sidebar
    from pygameweb.thumb.views import add_thumb_blueprint
    add_sidebar(app)
    add_user_blueprint(app)
    add_project_blueprint(app)
    add_thumb_blueprint(app)

    return client


def a_user(app, session, project_client, name, email,
           logged_in, disabled, active):
    """ gives us a user who is a member.
    """
    from pygameweb.user.models import User, Group
    from flask_security.utils import encrypt_password
    group = Group(name='members', title='Member')
    user = User(name=name,
                email=email,
                password=encrypt_password('password'),
                disabled=disabled,
                active=active,
                roles=[group])
    session.add(user)
    session.commit()

    # https://flask-login.readthedocs.org/en/latest/#fresh-logins
    with project_client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True
    return user


@pytest.fixture
def user(app, session, project_client):
    """ gives us a user who is a member.
    """
    return a_user(app, session, project_client, 'joe', 'asdf@example.com',
                  logged_in=True,
                  disabled=0,
                  active=True)


@pytest.fixture
def user_banned(app, session, project_client):
    """ gives us a user who is a member.
    """
    return a_user(app, session, project_client,
                  'joebanned',
                  'asdf2@example.com',
                  logged_in=False,
                  disabled=1,
                  active=False)


@pytest.fixture
def project(session, user):
    """ links up a Project with releases, tags, and comments for testing.
    """
    import datetime
    from pygameweb.project.models import Project, Release, Projectcomment, Tags

    the_project = Project(
        title='Some project title 1',
        summary='Summary of some project 1.',
        description='Description of some project.',
        uri='http://some.example.com/',
        datetimeon=datetime.datetime(2017, 1, 5),
        image='1.png',
        youtube_trailer='https://www.youtube.com/watch?v=8UnvMe1Neok',
        github_repo='https://github.com/pygame/pygameweb/',
        patreon='https://www.patreon.com/pygame',
        user=user
    )

    tag1 = Tags(project=the_project, value='game')
    tag2 = Tags(project=the_project, value='arcade')
    session.add(tag1)
    session.add(tag2)

    release1 = Release(datetimeon=datetime.datetime(2017, 1, 5),
                       description='Some release.',
                       srcuri='http://example.com/source.tar.gz',
                       winuri='http://example.com/win.exe',
                       macuri='http://example.com/mac.dmg',
                       version='A release title.')

    release2 = Release(datetimeon=datetime.datetime(2017, 1, 6),
                       description='Some release with new things.',
                       srcuri='http://example.com/source.tar.gz',
                       winuri='http://example.com/win.exe',
                       macuri='http://example.com/mac.dmg',
                       version='A second release title.')

    the_project.releases.append(release1)
    the_project.releases.append(release2)

    comment1 = Projectcomment(user=user, content="Some comment 1.", rating=5)
    comment2 = Projectcomment(user=user, content="Some comment 2.", rating=3)
    the_project.comments.append(comment1)
    the_project.comments.append(comment2)

    session.add(the_project)
    session.commit()
    return the_project


def a_project(session, title, release_description, version, user):
    """ adds a second project with a couple of tags.
    """

    import datetime
    from pygameweb.project.models import Project, Tags, Release

    the_project2 = Project(
        title=title,
        summary='Summary of some project 2.',
        description='Description of some project 2.',
        uri='http://some.example.com/',
        datetimeon=datetime.datetime(2017, 1, 8),
        image='1.png',
        user=user
    )

    release1 = Release(datetimeon=datetime.datetime(2017, 1, 5),
                       description=release_description,
                       srcuri='http://example.com/source.tar.gz',
                       winuri='http://example.com/win.exe',
                       macuri='http://example.com/mac.dmg',
                       version=version)

    the_project2.releases.append(release1)

    tag3 = Tags(project=the_project2, value='2d')
    tag4 = Tags(project=the_project2, value='arcade')
    return the_project2, release1, tag3, tag4


@pytest.fixture
def project2(session, project, user):
    """ adds a second project with a couple of tags.
    """
    title = 'Some project title 2'
    version = 'some version'
    release_description = 'release description 2'
    (the_project2,
     release1,
     tag3,
     tag4) = a_project(session, title, release_description, version, user)

    session.add(release1)
    session.add(tag3)
    session.add(tag4)
    session.add(the_project2)
    return the_project2


@pytest.fixture
def project3(session, project, user_banned):
    """ adds a second project with a couple of tags.
    """
    title = 'Some project title 3'
    version = 'some version 3'
    release_description = 'release description 3'
    (the_project3,
     release1,
     tag3,
     tag4) = a_project(session, title, release_description, version, user_banned)

    session.add(the_project3)
    session.add(release1)
    session.add(tag3)
    session.add(tag4)
    return the_project3


def test_project_hidden(project_client, session, project, project2, project3):
    """ when user account has been disabled.
    """
    from pygameweb.project.models import Project, Tags, Release
    from pygameweb.user.models import User, Group

    session.flush()

    resp = project_client.get(f'/project/{project.id}/')
    assert resp.status_code == 200
    resp = project_client.get(f'/project/{project3.id}/')
    assert resp.status_code == 404

    resp = project_client.get('/tags/all')
    assert b'Some project title 3' not in resp.data, 'because user is banned'

    resp = project_client.get('/tags/arcade')
    assert resp.status_code == 200
    assert project.title.encode('utf-8') + b'</a>' in resp.data
    assert (project2.title.encode('utf-8') +
            b'</a>') in resp.data, 'because both are in arcade.'

    assert b'Some project title 3</a>' not in resp.data, 'because user is banned'


def test_project_index(project_client, session, user, project, project2):
    """ is shown as the default.
    """
    assert project.releases
    assert project.tags
    assert project.comments
    assert project.user
    assert project.user.projects
    assert project.user.projectcomments
    assert project.tag_counts == [('arcade', 2, 16), ('game', 1, 14)]

    resp = project_client.get(f'/project/{project.id}/')
    assert resp.status_code == 200
    assert b'<h1>Some project title 1' in resp.data
    assert b'<h1>Some project title 2' not in resp.data
    assert project.description.encode('utf8') in resp.data
    assert b'game' in resp.data
    assert b'arcade' in resp.data

    resp = project_client.get(f'/project-blabla+bla-{project.id}-.html')
    assert resp.status_code == 200, 'because this url works too.'
    assert b'<h1>Some project title 1' in resp.data

    url = f'/project/{project.id}/{project.releases[0].id}'
    resp = project_client.get(url)
    assert resp.status_code == 200
    assert b'A release title.' in resp.data
    assert b'Some release.' in resp.data

    url = (f'/project-blabla+blasbla+-'
           f'{project.id}-{project.releases[0].id}.html')
    resp = project_client.get(url)
    assert resp.status_code == 200, 'because this url works too.'
    assert b'A release title.' in resp.data

    assert b'twitter:card' in resp.data
    assert b'twitter:site' in resp.data
    assert b'twitter:creator' in resp.data
    assert b'og:url' in resp.data
    assert b'og:title' in resp.data
    assert b'og:description' in resp.data
    # assert b'og:image' in resp.data

    resp = project_client.get('/project/66/')
    assert resp.status_code == 404, 'when the project is not there'
    resp = project_client.get('/project/1/66')
    assert resp.status_code == 404, 'when the release is not there either'


def test_tags(project_client, session, project, project2):
    """ shows a list of projects for that tag.
    """
    session.commit()
    resp = project_client.get('/tags/game')
    assert resp.status_code == 200
    assert project.title.encode('utf-8') + b'</a>' in resp.data
    assert (project2.title.encode('utf-8') +
            b'</a>') not in resp.data, 'because only first tagged.'

    resp = project_client.get('/tags/arcade')
    assert resp.status_code == 200
    assert project.title.encode('utf-8') + b'</a>' in resp.data
    assert (project2.title.encode('utf-8') +
            b'</a>') in resp.data, 'because both are in arcade.'

    resp = project_client.get('/tags/all')
    assert (resp.status_code ==
            200), 'because all is a special tag meaning show all.'
    assert project.title.encode('utf-8') + b'</a>' in resp.data
    assert (project2.title.encode('utf-8') +
            b'</a>') in resp.data, 'both are in all'

    assert project_client.get('/tags/').status_code == 200, 'big list of tags'
    assert project_client.get('/tags').status_code == 200


def test_new_project_page(project_client, user):
    """ tests the page to create a new project.
    """
    resp = project_client.get('/members/projects/new')
    assert resp.status_code == 200

    # Ensures the presence of the input labels
    input_labels = [
        b'New Project',
        b'Tags',
        b'image',
        b'Summary',
        b'Description',
        b'Home URL',
        b'version',
        b'Windows URL',
        b'Mac URL'
    ]
    for label in input_labels:
        assert (label in resp.data), f'label {label} not present in page.'


def test_add_new_project(config, project_client, session, user):
    """ adds a new project for the user.
    """
    from io import BytesIO
    from pygameweb.project.models import Project, Tags

    png = (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
           b'\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT'
           b'\x08\x99c```\x00\x00\x00\x04\x00\x01\xa3\n\x15\xe3\x00\x00'
           b'\x00\x00IEND\xaeB`\x82')

    image = (BytesIO(png), 'helloworld.png')
    data = dict(
        image=image,
        title='title',
        version='1.0.2',
        tags='tags',
        summary='summary',
        description='description of project',
        uri='http://example.com/',
        youtube_trailer='https://www.youtube.com/watch?v=8UnvMe1Neok',
        github_repo='https://github.com/pygame/pygameweb/',
        patreon='https://www.patreon.com/pygame',
    )

    with mock.patch('pygameweb.project.views.save_image') as save_image:
        resp = project_client.post('/members/projects/new',
                                   data=data,
                                   follow_redirects=True)
        project = (session
                   .query(Project)
                   .filter(Project.title == 'title')
                   .first())
        assert (str(Path(f'{config.WWW}/shots/{project.id}.png')) ==
                save_image.call_args[0][1])
        resp = project_client.get(f'/project/{project.id}/')
        assert project.description.encode('utf8') in resp.data

        project.youtube_trailer == data['youtube_trailer']
        project.github_repo == data['github_repo']
        project.patreon == data['patreon']

    assert resp.status_code == 200
    assert project.title == 'title'
    assert project.releases[0].version == '1.0.2', 'a release was added too'

    url = f'/members/projects/edit/{project.id}'
    resp = project_client.get(url)
    assert resp.status_code == 200

    image = (BytesIO(png), 'helloworld.png')
    data = dict(image=image, title='titlechanged',
                tags='tag1, tag2, tag3', summary='summary',
                description='description', uri='http://example.com/')

    with mock.patch('pygameweb.project.views.save_image') as save_image:
        resp = project_client.post(f'/members/projects/edit/{project.id}',
                                   data=data,
                                   follow_redirects=True)
        project = (session
                   .query(Project)
                   .filter(Project.title == 'titlechanged')
                   .first())
        assert (str(Path(f'{config.WWW}/shots/{project.id}.png')) ==
                save_image.call_args[0][1])

    data = dict(title='titlechangedagain',
                tags='tag1, tag2, tag3', summary='summary',
                description='description', uri='http://example.com/')

    with mock.patch('pygameweb.project.views.save_image') as save_image:
        resp = project_client.post(f'/members/projects/edit/{project.id}',
                                   data=data,
                                   follow_redirects=True)
        project = (session
                   .query(Project)
                   .filter(Project.title == 'titlechangedagain')
                   .first())
        assert not save_image.called, 'no image sent or saved'

        tags = (session
                .query(Tags)
                .filter(Tags.project_id == project.id)
                .all())
        assert len(tags) == 3
        assert [tag.value for tag in tags] == ['tag1', 'tag2', 'tag3']

    url = f'/members/projects/{project.id}/releases/new'
    resp = project_client.get(url)
    assert resp.status_code == 200

    data = dict(description='updated description',
                version='2.0.0',
                srcuri='http://example.com/')

    release = project.releases[0]
    url = f'/members/projects/{project.id}/releases/edit/{release.id}'
    resp = project_client.post(url, data=data, follow_redirects=True)
    assert resp.status_code == 200

    session.refresh(project)
    session.refresh(project.releases[0])
    assert data['description'] == project.releases[0].description
    assert project.releases[0].version == '2.0.0', 'edited a release version'
    assert len(project.releases) == 1

    data = dict(description='new release',
                version='3.0.0',
                srcuri='http://example.com/')
    url = f'/members/projects/{project.id}/releases/new'
    resp = project_client.post(url, data=data, follow_redirects=True)
    assert resp.status_code == 200
    session.refresh(project)
    assert len(project.releases) == 2
    assert project.releases[1].version == '3.0.0', 'we added a release version'

    url = f'/members/projects/{project.id}/releases'
    resp = project_client.get(url)
    assert resp.status_code == 200

    resp = project_client.get('/members/projects')
    assert resp.status_code == 200


def test_add_new_project_without_image(project_client, session, user):
    """ adds a new project for the user without an image.
    """
    from pygameweb.project.models import Project, Tags

    data = dict(
        title='title',
        version='1.0.2',
        tags='tags',
        summary='summary',
        description='description of project',
        uri='http://example.com/',
        youtube_trailer='https://www.youtube.com/watch?v=8UnvMe1Neok',
        github_repo='https://github.com/pygame/pygameweb/',
        patreon='https://www.patreon.com/pygame',
    )

    with mock.patch('pygameweb.project.views.save_image') as save_image:
        resp = project_client.post('/members/projects/new',
                                   data=data,
                                   follow_redirects=True)
        project = (session
                   .query(Project)
                   .filter(Project.title == 'title')
                   .first())
        assert not save_image.called, 'no image sent or saved'

        resp = project_client.get(f'/project/{project.id}/')
        assert project.description.encode('utf8') in resp.data

        project.youtube_trailer == data['youtube_trailer']
        project.github_repo == data['github_repo']
        project.patreon == data['patreon']

    assert resp.status_code == 200
    assert project.title == 'title'
    assert project.releases[0].version == '1.0.2', 'a release was added too'

    url = f'/members/projects/edit/{project.id}'
    resp = project_client.get(url)
    assert resp.status_code == 200

    data = dict(title='titlechanged',
                tags='tag1, tag2, tag3', summary='summary',
                description='description', uri='http://example.com/')

    with mock.patch('pygameweb.project.views.save_image') as save_image:
        resp = project_client.post(f'/members/projects/edit/{project.id}',
                                   data=data,
                                   follow_redirects=True)
        project = (session
                   .query(Project)
                   .filter(Project.title == 'titlechanged')
                   .first())
        assert not save_image.called, 'no image sent or saved'

    data = dict(title='titlechangedagain',
                tags='tag1, tag2, tag3', summary='summary',
                description='description', uri='http://example.com/')

    with mock.patch('pygameweb.project.views.save_image') as save_image:
        resp = project_client.post(f'/members/projects/edit/{project.id}',
                                   data=data,
                                   follow_redirects=True)
        project = (session
                   .query(Project)
                   .filter(Project.title == 'titlechangedagain')
                   .first())
        assert not save_image.called, 'no image sent or saved'

        tags = (session
                .query(Tags)
                .filter(Tags.project_id == project.id)
                .all())
        assert len(tags) == 3
        assert [tag.value for tag in tags] == ['tag1', 'tag2', 'tag3']

    url = f'/members/projects/{project.id}/releases/new'
    resp = project_client.get(url)
    assert resp.status_code == 200

    data = dict(description='updated description',
                version='2.0.0',
                srcuri='http://example.com/')

    release = project.releases[0]
    url = f'/members/projects/{project.id}/releases/edit/{release.id}'
    resp = project_client.post(url, data=data, follow_redirects=True)
    assert resp.status_code == 200

    session.refresh(project)
    session.refresh(project.releases[0])
    assert data['description'] == project.releases[0].description
    assert project.releases[0].version == '2.0.0', 'edited a release version'
    assert len(project.releases) == 1

    data = dict(description='new release',
                version='3.0.0',
                srcuri='http://example.com/')
    url = f'/members/projects/{project.id}/releases/new'
    resp = project_client.post(url, data=data, follow_redirects=True)
    assert resp.status_code == 200
    session.refresh(project)
    assert len(project.releases) == 2
    assert project.releases[1].version == '3.0.0', 'we added a release version'

    url = f'/members/projects/{project.id}/releases'
    resp = project_client.get(url)
    assert resp.status_code == 200

    resp = project_client.get('/members/projects')
    assert resp.status_code == 200


def test_new_project_comment(project_client, session, project, project2, user):
    """ adds the thoughtful and supportive comment to the project page for the
        interesting creative work someone is trying to share with the world.
    """
    with mock.patch('pygameweb.project.views.classify_comment'):

        url = f'/project/{project.id}/comment'
        data = {'message':
                '<p>Gidday matey. Keeping busy are ya? This. Is. Awesome.</p>'}
        resp = project_client.post(url, data=data, follow_redirects=True)
        assert resp.status_code == 200
        assert (b'Gidday matey.' in
                resp.data), 'because the comment should be there.'

@pytest.mark.parametrize("feed_url", [
    '/feed/releases.php?format=ATOM',
    '/feed/releases.php?format=RSS2.0',
    '/project/feed/rss',
    '/project/feed/atom'
])
def test_feeds(project_client, session, project, project2, feed_url):
    resp = project_client.get(feed_url)
    assert resp.status_code == 200
