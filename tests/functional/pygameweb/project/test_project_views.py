import pytest


@pytest.fixture
def project_client(app, session, client):
    """Fixture for wiki tests.
    """
    from pygameweb.project.views import add_project_blueprint

    add_project_blueprint(app)
    return client


@pytest.fixture
def user(session):
    from pygameweb.user.models import User
    user = User(name='joe')
    session.add(user)
    return user


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


@pytest.fixture
def project2(session, project, user):

    import datetime
    from pygameweb.project.models import Project, Release, Projectcomment, Tags
    from pygameweb.user.models import User

    the_project2 = Project(
        title='Some project title 2',
        summary='Summary of some project 2.',
        description='Description of some project 2.',
        uri='http://some.example.com/',
        datetimeon=datetime.datetime(2017, 1, 8),
        image='1.png',
        user=user
    )

    tag3 = Tags(project=the_project2, value='2d')
    tag4 = Tags(project=the_project2, value='arcade')
    session.add(tag3)
    session.add(tag4)
    session.add(the_project2)
    return the_project2



def test_project_index(project_client, session, project, project2):
    """ is shown as the default.
    """
    assert project.releases
    assert project.tags
    assert project.comments
    assert project.user
    assert project.user.projects
    assert project.user.projectcomments
    assert project.tag_counts == [('arcade', 2, 16), ('game', 1, 14)]

    resp = project_client.get('/project/1')
    assert resp.status_code == 200
    assert b'Some project title 1' in resp.data
    assert b'Some project title 2' not in resp.data
    assert b'game' in resp.data
    assert b'arcade' in resp.data

    resp = project_client.get('/project/1/1')
    assert resp.status_code == 200
    assert b'A release title.' in resp.data
    print(resp.data.decode('utf-8'))



def test_tags(project_client, session, project, project2):
    """ shows a list of projects for that tag.
    """
    from pygameweb.project.models import Project, Release, Projectcomment, Tags

    per_page = 30
    start = 0
    prev_start = max(start - per_page, 0)
    next_start = start + per_page

    projects = (session
                .query(Project)
                .filter(Tags.project_id == Project.id)
                .filter(Tags.value == 'arcade')
                .offset(start)
                .limit(per_page)
                .all())

    resp = project_client.get('/tags/game')
    assert resp.status_code == 200
    assert project.title.encode('utf-8') in resp.data
    assert project2.title.encode('utf-8') not in resp.data, 'only first is tagged game'

    resp = project_client.get('/tags/arcade')
    assert resp.status_code == 200
    assert project.title.encode('utf-8') in resp.data
    assert project2.title.encode('utf-8') in resp.data, 'both are in arcade'




def test_project_new(project_client, session):
    """ adds a new project for the user.
    """

    from io import BytesIO

    resp = project_client.get('/members/projects/new')
    assert resp.status_code == 200
    assert b'New Project' in resp.data
    assert b'Windows URL' in resp.data
    image = (BytesIO(b'my file contents'), 'hello world.png')
    data = dict(image=image, title='title', version='1.0.2',
                tags='tags', summary='summary',
                description='description', url='url')

    resp = project_client.post('/members/projects/new', data=data)
