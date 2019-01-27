""" For syncing github releases to pygame releases.
"""
import urllib.parse
import feedparser
import requests
import dateutil.parser

from pygameweb.project.models import Project, Release
from pygameweb.config import Config

def sync_github_releases():
    """ to the pygame website releases.
    """
    from pygameweb.config import Config
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

    a_connection = engine.connect()
    a_transaction = a_connection.begin()
    session = sessionmaker(bind=a_connection)()

    projects = (session
        .query(Project)
        .filter(Project.github_repo.isnot(None))
    )
    for project in projects:
        sync_project(session, project)

    session.commit()
    a_transaction.commit()


def sync_project(session, project):
    if not project.github_repo:
        return
    if project.user is not None and project.user.disabled:
        return
    gh_releases = get_gh_releases_feed(project)
    releases = project.releases

    gh_add, gh_update, pg_delete = releases_to_sync(gh_releases, releases)

    # only do the API call once if we need to add/update.
    releases_gh_api = (
        get_gh_releases_api(project)
        if gh_add or gh_update else None
    )

    releases_added = []
    for gh_release in gh_add:
        gh_release_api = [
            r for r in releases_gh_api
            if r['name'] == gh_release['title']
        ]
        if not gh_release_api or gh_release_api[0]['draft']:
            continue

        release = release_from_gh(session, project, gh_release, gh_release_api[0])
        releases_added.append(release)

    for release in releases_added:
        session.add(release)

    for gh_release in gh_update:
        releases = [
            r for r in project.releases
            if r.version == gh_release['title']
        ]
        if releases:
            release = releases[0]

            release.version = gh_release['title']
            release.description = gh_release['body']
            session.add(release)

    for pg_release in pg_delete:
        pg_release.delete()
        session.add(pg_release)


def release_from_gh(session, project, gh_release_atom, gh_release_api):
    """ make a Release from a gh release.

    :param gh_release_atom: from the atom feed.
    :param gh_release_api: from the API.
    """
    winuri = ''
    srcuri = ''
    macuri = ''
    for asset in gh_release_api['assets']:
        if asset["browser_download_url"].endswith('msi'):
            winuri = asset["browser_download_url"]
        elif asset["browser_download_url"].endswith('tar.gz'):
            srcuri = asset["browser_download_url"]
        elif asset["browser_download_url"].endswith('dmg'):
            macuri = asset["browser_download_url"]

    published_at = dateutil.parser.parse(gh_release_api["published_at"])
    # "2019-01-06T15:29:18Z",

    release = Release(
        datetimeon=published_at,
        description=gh_release_atom['content'][0]["value"],
        srcuri=srcuri,
        winuri=winuri,
        macuri=macuri,
        version=gh_release_atom['title'],
        project=project
    )
    return release


def releases_to_sync(gh_releases, releases):
    """
    :param gh_releases: github release objects from atom.
    :param releases: the db releases.
    """
    add, update, delete = versions_to_sync(gh_releases, releases)

    gh_add = [r for r in gh_releases if r.title in add]
    gh_update = [r for r in gh_releases if r.title in update]
    pg_delete = [r for r in releases if r.version in delete]
    return gh_add, gh_update, pg_delete

def versions_to_sync(gh_releases, releases):
    """
    :param gh_releases: github release objects from atom.
    :param releases: the db releases.
    """
    # Because many projects might have existing ones on pygame,
    #  but not have them on github, we don't delete ones unless
    #  they came originally from github.
    return what_versions_sync(
        {r.version for r in releases},
        {r.title for r in gh_releases},
        {r.version for r in releases if r.from_external == 'github'}
    )

def what_versions_sync(pg_versions, gh_versions, pg_versions_gh):
    """ versions to add, update, delete.
    """
    to_add = gh_versions - pg_versions
    to_update = pg_versions_gh & gh_versions
    to_delete = pg_versions_gh - gh_versions
    return to_add, to_update, to_delete

def get_gh_releases_feed(project):
    """ for a project.
    """
    repo = project.github_repo
    if not repo.endswith('/'):
        repo += '/'
    feed_url = urllib.parse.urljoin(
        repo,
        "releases.atom"
    )
    data = feedparser.parse(feed_url)
    if not data['feed']['title'].startswith('Release notes from'):
        raise ValueError('does not appear to be a github release feed.')
    return data.entries


def get_repo_from_url(url):
    """ get the github repo from the url
    """
    if not url.startswith('https://github.com/'):
        return
    repo = (
        urllib.parse.urlparse(url).path
        .lstrip('/')
        .rstrip('/')
    )
    if len(repo.split('/')) != 2:
        return
    return repo


def get_gh_releases_api(project, version=None):
    """
    """
    # https://developer.github.com/v3/auth/
    # self.headers = {'Authorization': 'token %s' % self.api_token}
    # https://api.github.com/repos/pygame/stuntcat/releases/latest
    repo = get_repo_from_url(project.github_repo)
    if not repo:
        return

    url = f'https://api.github.com/repos/{repo}/releases'
    if version is not None:
        url += f'/{version}'

    if Config.GITHUB_RELEASES_OAUTH is None:
        headers = {}
    else:
        headers = {'Authorization': 'token %s' % Config.GITHUB_RELEASES_OAUTH}
    resp = requests.get(
        url,
        headers = headers
    )
    if resp.status_code != 200:
        raise ValueError('github api failed')

    data = resp.json()
    return data




