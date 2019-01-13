""" For syncing github releases to pygame releases.
"""
import urllib.parse
import feedparser


# def sync_project(session, project):
#     if not project.github_repo:
#         return
#     gh_releases = get_gh_releases(project)
#     releases = project.releases
#     gh_add, gh_update, pg_delete = releases_to_sync(gh_releases, releases)

#     #TODO: deal with gh_add, gh_update, pg_delete
#     for gh_release in gh_add:
#         session.add(release_from_gh(gh_release))

#     for gh_release in gh_update:
#         release = session. get Release     gh_release   ...
#         release.version = gh_release.title
#         release. changes = gh_release. xx
#         session.add(release)

#     for pg_release in pg_delete:
#         release = session. get Release   pg_release   ...
#         release.delete()
#         session.add(release)



# def release_from_gh(gh_release):
#     """ make a Release from a gh release.
#     """

#     ...



def releases_to_sync(gh_releases, releases):
    add, update, delete = versions_to_sync(gh_releases, releases)

    gh_add = [r for r in gh_releases if r.title in add]
    gh_update = [r for r in gh_releases if r.title in update]
    pg_delete = [r for r in releases if r.version in delete]
    return gh_add, gh_update, pg_delete

def versions_to_sync(gh_releases, releases):

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
