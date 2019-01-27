import pytest


class Release:
    def __init__(self, version, description, from_external):
        self.version = version
        self.description = description
        self.from_external = from_external


class GRelease:
    def __init__(self, title, content):
        self.title = title
        self.content = [{"value": content}]
        self.draft = False


def make_gh(releases):
    return [GRelease(r[0], r[1]) for r in releases]


def make_pg(releases):
    return [Release(r[0], r[1], r[2]) for r in releases]


def test_releases_to_sync():
    """ adds the one that is missing.
    """
    from pygameweb.project.gh_releases import releases_to_sync

    pg_releases = make_pg([("0.1", "r1", None), ("0.2", "r2", None)])
    gh_releases = make_gh([("0.1", "r1"), ("0.2", "r2"), ("0.3", "r3")])
    gh_add, gh_update, pg_delete = releases_to_sync(gh_releases, pg_releases)

    assert len(gh_add) == 1
    assert not gh_update and not pg_delete
    assert gh_add[0].title == "0.3"


def test_releases_to_sync_delete():
    """ deletes the github updated one that is there.
    """
    from pygameweb.project.gh_releases import releases_to_sync

    pg_releases = make_pg([("0.1", "r1", None), ("0.2", "r2", "github")])
    gh_releases = make_gh([("0.1", "r1")])
    gh_add, gh_update, pg_delete = releases_to_sync(gh_releases, pg_releases)

    assert not gh_add and not gh_update
    assert len(pg_delete) == 1
    assert pg_delete[0].version == "0.2"


def test_releases_to_sync_update():
    """ updates the github one that changed.
    """
    from pygameweb.project.gh_releases import releases_to_sync

    pg_releases = make_pg([("0.1", "r1", None), ("0.2", "r2", "github")])
    gh_releases = make_gh([("0.1", "r1"), ("0.2", "r2 with updated content")])
    gh_add, gh_update, pg_delete = releases_to_sync(gh_releases, pg_releases)

    assert len(gh_update) == 1
    assert not gh_add and not pg_delete
    assert gh_update[0].title == "0.2"
    assert gh_update[0].content[0]["value"] == "r2 with updated content"


#TODO: test a draft release.
#TODO: test sync_project deletes and updates releases properly.
#TODO: mock out real gh request.


def test_get_repo_from_url():
    """ gets the github repo from the url.
    """
    from pygameweb.project.gh_releases import get_repo_from_url

    url = "https://github.com/pygame/pygame/"
    assert get_repo_from_url(url) == "pygame/pygame"

    url = "https://github.com/pygame/pygame"
    assert get_repo_from_url(url) == "pygame/pygame"

    url = "xxx"
    assert get_repo_from_url(url) == None

    url = "https://github.com/pygame"
    assert get_repo_from_url(url) == None


@pytest.fixture
def project(session):
    """ links up a Project with releases, tags, and comments for testing.
    """
    import datetime
    from pygameweb.project.models import Project, Release, Projectcomment, Tags

    from pygameweb.user.models import User, Group

    user = User(name="name", email="email", password="", disabled=0, active=True)

    the_project = Project(
        title="Stuntcat",
        summary="Summary of some project 1.",
        description="Description of some project.",
        uri="http://some.example.com/",
        datetimeon=datetime.datetime(2017, 1, 5),
        image="1.png",
        github_repo="https://github.com/pygame/stuntcat",
        user=user,
    )

    tag1 = Tags(project=the_project, value="game")
    tag2 = Tags(project=the_project, value="arcade")
    session.add(tag1)
    session.add(tag2)

    release1 = Release(
        datetimeon=datetime.datetime(2017, 1, 5),
        description="Some release.",
        srcuri="http://example.com/source.tar.gz",
        winuri="http://example.com/win.exe",
        macuri="http://example.com/mac.dmg",
        version="A release title.",
    )

    release2 = Release(
        datetimeon=datetime.datetime(2017, 1, 6),
        description="Some release with new things.",
        srcuri="http://example.com/source.tar.gz",
        winuri="http://example.com/win.exe",
        macuri="http://example.com/mac.dmg",
        version="A second release title.",
    )

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
def gh_release_atom():
    import time
    return {
        "author": "illume",
        "author_detail": {"name": "illume"},
        "authors": [{"name": "illume"}],
        "content": [
            {
                "base": "https://github.com/pygame/stuntcat/releases.atom",
                "language": "en-US",
                "type": "text/html",
                "value": "<p>This release can install via pip on a lot more "
                "machines. Because pymunk binaries are now available "
                "for mac and linux.<br>\n"
                '<a target="_blank" rel="noopener noreferrer" '
                'href="https://raw.githubusercontent.com/pygame/stuntcat/master/docs/gameplay.gif"><img '
                'src="https://raw.githubusercontent.com/pygame/stuntcat/master/docs/gameplay.gif" '
                'style="max-width:100%;"></a></p>',
            }
        ],
        "guidislink": True,
        "href": "",
        "id": "tag:github.com,2008:Repository/159383958/0.0.13",
        "link": "https://github.com/pygame/stuntcat/releases/tag/0.0.13",
        "links": [
            {
                "href": "https://github.com/pygame/stuntcat/releases/tag/0.0.13",
                "rel": "alternate",
                "type": "text/html",
            }
        ],
        "media_thumbnail": [
            {
                "height": "30",
                "url": "https://avatars3.githubusercontent.com/u/9541?s=60&v=4",
                "width": "30",
            }
        ],
        "summary": "<p>This release can install via pip on a lot more machines. "
        "Because pymunk binaries are now available for mac and linux.<br>\n"
        '<a target="_blank" rel="noopener noreferrer" '
        'href="https://raw.githubusercontent.com/pygame/stuntcat/master/docs/gameplay.gif"><img '
        'src="https://raw.githubusercontent.com/pygame/stuntcat/master/docs/gameplay.gif" '
        'style="max-width:100%;"></a></p>',
        "title": "0.0.13",
        "title_detail": {
            "base": "https://github.com/pygame/stuntcat/releases.atom",
            "language": "en-US",
            "type": "text/plain",
            "value": "0.0.13",
        },
        "updated": "2019-01-07T09:20:56Z",
        "updated_parsed": time.struct_time((
            2019,
            1,
            7,
            9,
            20,
            56,
            0,
            7,
            0,
        )),
    }


@pytest.fixture
def gh_release_api():
    return {
        "assets": [
            {
                "browser_download_url": "https://github.com/pygame/stuntcat/releases/download/0.0.13/stuntcat-0.0.13-win32.msi",
                "content_type": "application/octet-stream",
                "created_at": "2019-01-05T11:04:28Z",
                "download_count": 2,
                "id": 10419315,
                "label": "",
                "name": "stuntcat-0.0.13-win32.msi",
                "node_id": "MDEyOlJlbGVhc2VBc3NldDEwNDE5MzE1",
                "size": 22106112,
                "state": "uploaded",
                "updated_at": "2019-01-05T11:04:30Z",
                "uploader": {
                    "avatar_url": "https://avatars3.githubusercontent.com/u/9541?v=4",
                    "events_url": "https://api.github.com/users/illume/events{/privacy}",
                    "followers_url": "https://api.github.com/users/illume/followers",
                    "following_url": "https://api.github.com/users/illume/following{/other_user}",
                    "gists_url": "https://api.github.com/users/illume/gists{/gist_id}",
                    "gravatar_id": "",
                    "html_url": "https://github.com/illume",
                    "id": 9541,
                    "login": "illume",
                    "node_id": "MDQ6VXNlcjk1NDE=",
                    "organizations_url": "https://api.github.com/users/illume/orgs",
                    "received_events_url": "https://api.github.com/users/illume/received_events",
                    "repos_url": "https://api.github.com/users/illume/repos",
                    "site_admin": False,
                    "starred_url": "https://api.github.com/users/illume/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/illume/subscriptions",
                    "type": "User",
                    "url": "https://api.github.com/users/illume",
                },
                "url": "https://api.github.com/repos/pygame/stuntcat/releases/assets/10419315",
            },
            {
                "browser_download_url": "https://github.com/pygame/stuntcat/releases/download/0.0.13/stuntcat-0.0.13.dmg",
                "content_type": "application/x-apple-diskimage",
                "created_at": "2019-01-05T11:08:36Z",
                "download_count": 1,
                "id": 10419329,
                "label": "",
                "name": "stuntcat-0.0.13.dmg",
                "node_id": "MDEyOlJlbGVhc2VBc3NldDEwNDE5MzI5",
                "size": 24125634,
                "state": "uploaded",
                "updated_at": "2019-01-05T11:08:37Z",
                "uploader": {
                    "avatar_url": "https://avatars3.githubusercontent.com/u/9541?v=4",
                    "events_url": "https://api.github.com/users/illume/events{/privacy}",
                    "followers_url": "https://api.github.com/users/illume/followers",
                    "following_url": "https://api.github.com/users/illume/following{/other_user}",
                    "gists_url": "https://api.github.com/users/illume/gists{/gist_id}",
                    "gravatar_id": "",
                    "html_url": "https://github.com/illume",
                    "id": 9541,
                    "login": "illume",
                    "node_id": "MDQ6VXNlcjk1NDE=",
                    "organizations_url": "https://api.github.com/users/illume/orgs",
                    "received_events_url": "https://api.github.com/users/illume/received_events",
                    "repos_url": "https://api.github.com/users/illume/repos",
                    "site_admin": False,
                    "starred_url": "https://api.github.com/users/illume/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/illume/subscriptions",
                    "type": "User",
                    "url": "https://api.github.com/users/illume",
                },
                "url": "https://api.github.com/repos/pygame/stuntcat/releases/assets/10419329",
            },
            {
                "browser_download_url": "https://github.com/pygame/stuntcat/releases/download/0.0.13/stuntcat-0.0.13.tar.gz",
                "content_type": "application/gzip",
                "created_at": "2019-01-05T11:08:38Z",
                "download_count": 1,
                "id": 10419331,
                "label": "",
                "name": "stuntcat-0.0.13.tar.gz",
                "node_id": "MDEyOlJlbGVhc2VBc3NldDEwNDE5MzMx",
                "size": 3084175,
                "state": "uploaded",
                "updated_at": "2019-01-05T11:08:38Z",
                "uploader": {
                    "avatar_url": "https://avatars3.githubusercontent.com/u/9541?v=4",
                    "events_url": "https://api.github.com/users/illume/events{/privacy}",
                    "followers_url": "https://api.github.com/users/illume/followers",
                    "following_url": "https://api.github.com/users/illume/following{/other_user}",
                    "gists_url": "https://api.github.com/users/illume/gists{/gist_id}",
                    "gravatar_id": "",
                    "html_url": "https://github.com/illume",
                    "id": 9541,
                    "login": "illume",
                    "node_id": "MDQ6VXNlcjk1NDE=",
                    "organizations_url": "https://api.github.com/users/illume/orgs",
                    "received_events_url": "https://api.github.com/users/illume/received_events",
                    "repos_url": "https://api.github.com/users/illume/repos",
                    "site_admin": False,
                    "starred_url": "https://api.github.com/users/illume/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/illume/subscriptions",
                    "type": "User",
                    "url": "https://api.github.com/users/illume",
                },
                "url": "https://api.github.com/repos/pygame/stuntcat/releases/assets/10419331",
            },
        ],
        "assets_url": "https://api.github.com/repos/pygame/stuntcat/releases/14815752/assets",
        "author": {
            "avatar_url": "https://avatars3.githubusercontent.com/u/9541?v=4",
            "events_url": "https://api.github.com/users/illume/events{/privacy}",
            "followers_url": "https://api.github.com/users/illume/followers",
            "following_url": "https://api.github.com/users/illume/following{/other_user}",
            "gists_url": "https://api.github.com/users/illume/gists{/gist_id}",
            "gravatar_id": "",
            "html_url": "https://github.com/illume",
            "id": 9541,
            "login": "illume",
            "node_id": "MDQ6VXNlcjk1NDE=",
            "organizations_url": "https://api.github.com/users/illume/orgs",
            "received_events_url": "https://api.github.com/users/illume/received_events",
            "repos_url": "https://api.github.com/users/illume/repos",
            "site_admin": False,
            "starred_url": "https://api.github.com/users/illume/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/illume/subscriptions",
            "type": "User",
            "url": "https://api.github.com/users/illume",
        },
        "body": "This release can install via pip on a lot more machines. Because "
        "pymunk binaries are now available for mac and linux.\r\n"
        "<img "
        'src="https://raw.githubusercontent.com/pygame/stuntcat/master/docs/gameplay.gif"/>',
        "created_at": "2019-01-05T10:25:13Z",
        "draft": False,
        "html_url": "https://github.com/pygame/stuntcat/releases/tag/0.0.13",
        "id": 14815752,
        "name": "0.0.13",
        "node_id": "MDc6UmVsZWFzZTE0ODE1NzUy",
        "prerelease": False,
        "published_at": "2019-01-06T15:29:18Z",
        "tag_name": "0.0.13",
        "tarball_url": "https://api.github.com/repos/pygame/stuntcat/tarball/0.0.13",
        "target_commitish": "4f72f73ea65f108e6abff7cab1692c6de4307b31",
        "upload_url": "https://uploads.github.com/repos/pygame/stuntcat/releases/14815752/assets{?name,label}",
        "url": "https://api.github.com/repos/pygame/stuntcat/releases/14815752",
        "zipball_url": "https://api.github.com/repos/pygame/stuntcat/zipball/0.0.13",
    }


def test_sync_project(session, project):
    """ when user account has been disabled.
    """
    from pygameweb.project.models import Project, Tags, Release
    from pygameweb.user.models import User, Group
    from pygameweb.project.gh_releases import sync_project

    sync_project(session, project)


#TODO: test that for disabled users it does not update the releases.

def test_release_from_gh(session, project, gh_release_atom, gh_release_api):
    """
    """
    from pygameweb.project.gh_releases import release_from_gh
    release = release_from_gh(session, project, gh_release_atom, gh_release_api)
