"""
"""


def test_a_wiki(session):

    from pygameweb.wiki.models import Wiki
    wiki_entry = Wiki()

    session.add(wiki_entry)
    session.commit()



# for i in range(1000):
#     print("""def test_a_wiki%s(session):

#     from pygameweb.wiki.models import Wiki
#     wiki_entry = Wiki()

#     session.add(wiki_entry)
#     session.commit()

# """ % i)
