
def test_render():
    """ renders the wiki code as suitable html.
    """
    from pygameweb.wiki.wiki import render

    assert render('') == ''
    assert render('[[link#section]]') == '<a href="/wiki/link#section">link</a>'
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
    code = _wiki_code('<code class="python">def my_code(x): return x + 1</code>')

    should_be = '<div class="highlight" style="background: #f8f8f8"><pre style="line-height: 125%;"><span></span><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">my_code</span>(x): <span style="color: #008000; font-weight: bold">return</span> x <span style="color: #666666">+</span> <span style="color: #666666">1</span>\n</pre></div>\n'
    assert should_be in code, 'because code should be annotated'
    assert '<html' not in code


def test_wiki_code_pre():
    """For our tinymce rich text editor, we need to wrap code
       tags inside of pre tags. However, rendering them looks
       kind of silly.
    """
    from pygameweb.wiki.wiki import _wiki_pre_code_clean, _wiki_code
    from pyquery import PyQuery as pq
    code = _wiki_code('<div><pre><code class="python">def my_code(x): return x + 1</code></pre></div>')
    pq_content = pq(code)
    pq_content = _wiki_pre_code_clean(pq_content)
    assert pq_content.outerHtml().startswith('<div><div class="highlight"')

    code = _wiki_code('<pre><code class="python">def my_code(x): return x + 1</code></pre>')
    pq_content = pq(code)
    pq_content = _wiki_pre_code_clean(pq_content)
    assert pq_content.outerHtml().startswith('<div class="highlight"')



def test_wiki_link():
    """turns the markup using [] into a html anchor tag.
    """
    from pygameweb.wiki.wiki import _wiki_link
    should_be = '<a href="/wiki/link#section">link</a>'
    assert _wiki_link('[[link#section]]') == should_be


def test_wiki_section():
    from pygameweb.wiki.wiki import _wiki_section
    content = """

    <h1>Hello there matey</h1>
    Pleasure in other peoples leasure.

    <h2>Another section, another day</h2>
    Pleasure in other peoples leasure.

    <h3>Three levels deep</h3>
    On top of Prenzlauer Berg Berg.

    <h2>And finally the last one</h2>

    """
    res = _wiki_section(content).outerHtml()
    assert '<h1 id="Hello there matey"' in res, 'because headers should have an id'
    assert '<h2 id="Another section, another day"' in res


def test_wiki_section_h3():
    """What if there are no h1/h2 headers?
    """
    from pygameweb.wiki.wiki import _wiki_section
    content = """
    <h3>Hello there matey</h3>
    Pleasure in other peoples leasure.

    <h3>Another section, another day</h3>
    Pleasure in other peoples leasure.

    <h4>Three levels deep</h4>
    On top of Prenzlauer Berg Berg.

    <h3>And finally the last one</h3>
    """
    res = _wiki_section(content).outerHtml()
    assert '<h3 id="Hello there matey"' in res, 'because headers should have an id'
    assert '<h3 id="Another section, another day"' in res
