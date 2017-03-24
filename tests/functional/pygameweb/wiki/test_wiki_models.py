"""
"""


def test_wiki_models_new_version(session):
    """ creates a new version of the existing page.
    """
    import datetime
    from pygameweb.wiki.models import Wiki
    link = 'somelink'
    first_edit = datetime.datetime(2017, 1, 1)
    wiki_entry = Wiki(link=link,
                      title='some title',
                      content='some content',
                      datetimeon=first_edit,
                      latest=1)

    session.add(wiki_entry)
    session.commit()

    what_changed = 'changed some stuff'
    assert wiki_entry.id
    old_id = wiki_entry.id
    wiki_entry.new_version(session)
    wiki_entry.changes = what_changed
    session.commit()

    assert old_id != wiki_entry.id, 'we see we have a new database row.'

    new_one = (session
               .query(Wiki)
               .filter(Wiki.link == link)
               .filter(Wiki.latest == 1)
               .first())
    assert new_one.changes == what_changed, 'double check it is ok'
    assert new_one.datetimeon > first_edit, 'date updated'

    pages = (session
             .query(Wiki)
             .filter(Wiki.link == link)
             .all())

    assert len(pages) == 2
    assert [p.id for p in pages].count(old_id) == 1
    latest_list = [p.latest for p in pages]
    assert latest_list.count(1) == 1
    assert latest_list.count(0) == 1, 'old one is there with latest set to 0'
