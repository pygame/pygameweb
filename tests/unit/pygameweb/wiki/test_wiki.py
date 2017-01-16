
def test_render():
    """ renders the wiki code as suitable html.
    """
    from pygameweb.wiki.wiki import render

    assert render('') == ''
    assert render('[[link#section]]') == '<a href="//pygame.org/wiki/link?parent=">link</a>'


def test_wiki_img():
    """Returns the changed html for an img tag.
    """

    from pygameweb.wiki.wiki import _wiki_img
    assert (_wiki_img('<img src="image.gif" width=120 height=80>')
            == '<a href="image.gif?action=edit&parent=">'
               '<img src="image.gif?action=view&width=width=120&height=height=80"'
               ' width=120 height=80></a>')

    assert (_wiki_img('<img src="https://travis-ci.org/illume/pygame.png?branch=master"'
                      ' width=120 height=80>')
            == '<img src="https://travis-ci.org/illume/pygame.png?branch=master"'
               ' width=120 height=80>')


def test_wiki_href():
    """Gives us marked up code for a href.
    """
    from pygameweb.wiki.wiki import _wiki_href
    assert _wiki_href('<a href="link">') == '<a href="link?parent=">'


def test_wiki_code():
    from pygameweb.wiki.wiki import _wiki_code
    # import pdb;pdb.set_trace()
    assert (_wiki_code('<code class="python">my_code()</code>') ==
            '<div class="highlight"><pre><span></span>'
            '<span class="n">my_code</span><span class="p">()</span>\n</pre></div>\n')


def test_wiki_link():
    """turns the markup using [] into a html anchor tag.
    """
    from pygameweb.wiki.wiki import _wiki_link
    assert _wiki_link('[[link#section]]') == '<a href="//pygame.org/wiki/link?parent=">link</a>'

