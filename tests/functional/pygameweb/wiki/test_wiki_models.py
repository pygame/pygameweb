"""
"""


def test_a_wiki(session):

    from pygameweb.wiki.models import Wiki
    wiki_entry = Wiki()

    session.add(wiki_entry)
    session.commit()
