""" For syncing github releases to pygame releases.
"""
import feedparser
import urllib.parse

def sync_project(project):
    if not project.github_repo:
        return
    gh_releases = get_gh_releases(project)
    # get ones not as pygame project releases.
    gh_versions = {r.title for r in gh_releases}
    pg_versions = {r.version for r project.releases}
    versions_to_add = pg_versions - gh_versions

    gh_releases_to_add = [r for r in gh_releases if r.title in versions_to_add]

    # TODO: pg releases with from_external == 'github' can be updated.
    # gh_releases_to_update =
    raise NotImplmentedError()


def get_gh_releases(project):
    """ for a project.
    """
    repo = project.github_repo
    if not repo.endswith('/'):
        repo += '/'
    feed_url = urllib.parse.urljoin(
        project.github_repo,
        "releases.atom"
    )
    data = feedparser.parse(feed_url)
    if not data['title'].starts_with('Release notes from'):
        raise ValueError('does not appear to be a github release feed.')
    return data.entries

