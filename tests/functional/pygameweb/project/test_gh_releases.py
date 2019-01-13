
import pytest


class Release:
    def __init__(self, version, description, from_external):
        self.version = version
        self.description = description
        self.from_external = from_external

class GRelease:
    def __init__(self, title, content):
        self.title = title
        self.content = [{'value': content}]

def make_gh(releases):
    return [GRelease(r[0], r[1]) for r in releases]

def make_pg(releases):
    return [Release(r[0], r[1], r[2]) for r in releases]


def test_releases_to_sync():
    """ adds the one that is missing.
    """
    from pygameweb.project.gh_releases import releases_to_sync
    pg_releases = make_pg([('0.1', 'r1', None), ('0.2', 'r2', None)])
    gh_releases = make_gh([('0.1', 'r1'), ('0.2', 'r2'), ('0.3', 'r3')])
    gh_add, gh_update, pg_delete = releases_to_sync(gh_releases, pg_releases)

    assert len(gh_add) == 1
    assert not gh_update and not pg_delete
    assert gh_add[0].title == '0.3'

def test_releases_to_sync_delete():
    """ deletes the github updated one that is there.
    """
    from pygameweb.project.gh_releases import releases_to_sync

    pg_releases = make_pg([('0.1', 'r1', None), ('0.2', 'r2', 'github')])
    gh_releases = make_gh([('0.1', 'r1')])
    gh_add, gh_update, pg_delete = releases_to_sync(gh_releases, pg_releases)

    assert not gh_add and not gh_update
    assert len(pg_delete) == 1
    assert pg_delete[0].version == '0.2'

def test_releases_to_sync_update():
    """ updates the github one that changed.
    """
    from pygameweb.project.gh_releases import releases_to_sync

    pg_releases = make_pg([('0.1', 'r1', None), ('0.2', 'r2', 'github')])
    gh_releases = make_gh([('0.1', 'r1'), ('0.2', 'r2 with updated content')])
    gh_add, gh_update, pg_delete = releases_to_sync(gh_releases, pg_releases)

    assert len(gh_update) == 1
    assert not gh_add and not pg_delete
    assert gh_update[0].title == '0.2'
    assert gh_update[0].content[0]['value'] == 'r2 with updated content'
