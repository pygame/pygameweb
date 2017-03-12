
def test_render():
    """ renders the wiki code as suitable html.
    """
    from pygameweb.wiki.wiki import render

    assert render('') == ''
    assert render('[[link#section]]') == '<a href="//pygame.org/wiki/link?parent=">link</a>'
    assert (render('<div><table><tr><td>asdf</td></tr></table></div>') ==
            '<div><div class="table-responsive"><table class="table"><tr><td>asdf</td></tr></table></div></div>')
    assert (render('<div><a href="asdf">asdf</a></div>') ==
            '<div><a href="asdf?parent=" rel="nofollow">asdf</a></div>')

    table = """
        <div><table border="0">
                <tbody><tr>
                <td><a href="about?parent=" rel="nofollow">About</a><br/>
                </td><td><a href="FrequentlyAskedQuestions?parent=" rel="nofollow">FAQ</a><br/>
                </td><td><a href="info?parent=" rel="nofollow">Help (irc, lists)</a><br/>
                </td><td><a href="tutorials?parent=" rel="nofollow">Tutorials</a><br/>
                </td><td><a href="resources?parent=" rel="nofollow">Resources</a><br/>
                </td><td><a href="interviews?parent=" rel="nofollow">Interviews</a><br/>
                </td></tr></tbody>
            </table></div>
    """
    assert ('<div class="table-responsive"><table border="0" class="table">' in
            render(table))


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
    assert (_wiki_code('<code class="python">my_code()</code>') ==
            '<div class="highlight"><pre><span></span>'
            '<span class="n">my_code</span><span class="p">()</span>\n</pre></div>\n')


def test_wiki_link():
    """turns the markup using [] into a html anchor tag.
    """
    from pygameweb.wiki.wiki import _wiki_link
    assert _wiki_link('[[link#section]]') == '<a href="//pygame.org/wiki/link?parent=">link</a>'


def test_wiki_section():
    from pygameweb.wiki.wiki import _wiki_section
    content = """

    <h1>Hello there matey</h1>
    Pleasure in other peoples leasure.

    <h2>Another section, another day</h2>
    Pleasure in other peoples leasure.
    """
    res = _wiki_section(content).outerHtml()
    assert '<h1 id="Hello there matey">' in res, 'because headers should have an id'
    assert '<h2 id="Another section, another day">' in res

