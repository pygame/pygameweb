"""
"""


def test_a_wiki(session):

    from pygameweb.wiki.models import Wiki
    wiki_entry = Wiki()

    session.add(wiki_entry)
    session.commit()


def test_new_wiki_page(session):
    """ creates a new version of the existing page.
    """

    from pygameweb.wiki.models import Wiki
    link = 'somelink'
    wiki_entry = Wiki(link=link, title='some title', content='some content', latest=1)

    session.add(wiki_entry)
    session.commit()


    what_changed = 'changed some stuff'
    assert wiki_entry.id
    old_id = wiki_entry.id
    wiki_entry.new_version(session)
    wiki_entry.changes = what_changed
    session.commit()

    # we see we have a new database row.
    assert old_id != wiki_entry.id


    # double check it's ok when we query it.
    new_one = (session
               .query(Wiki)
               .filter(Wiki.link == link)
               .filter(Wiki.latest == 1)
               .first())
    assert new_one.changes == what_changed

    pages = (session
             .query(Wiki)
             .filter(Wiki.link == link)
             .all())

    assert len(pages) == 2
    assert [p.id for p in pages].count(old_id) == 1
    assert [p.latest for p in pages].count(1) == 1
    assert [p.latest for p in pages].count(0) == 1, 'the old one is there too with latest set to 0'


# for i in range(1000):
#     print("""def test_a_wiki%s(session):

#     from pygameweb.wiki.models import Wiki
#     wiki_entry = Wiki()

#     session.add(wiki_entry)
#     session.commit()

# """ % i)
