"""Wiki related code.

This works with basic html as the markup format as found on pygame.org


There are still a few items that need to be ported so all existing
content in the wiki will work ok. This involves giving the wiki rendering
code db access to look up other wiki content.

Note, that the output of this needs to be run through html sanitizers.
"""

import sys
import re

from pyquery import PyQuery as pq

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


_wiki_parent = ""


#img -- <img src="image.gif" width=120 height=80>
def _wiki_img(content):
    """
    """
    return re.sub(r'\<img(.*?)src\s*\=\s*\"([^"]+)\"(.*?)\>',
                  _wiki_img_callback, content, flags=re.I)

def _wiki_img_callback(matchobj):
    global _wiki_parent
    m = matchobj.groups()
    params = ""
    for k in ["width", "height"]:
        matches = re.search(k + r'\s*=\s*"*([0-9]+)"*', m[2], flags=re.I)

        if matches:
            params += '&' + k + '=%s' % matches.group()
    if m[1].lower().startswith("http"):
        return '<img' + m[0] + 'src="' + m[1] + '"' + m[2] + '>'
    else:

        # return '<a href="' + m[1] + '?action=edit&parent=' + _wiki_parent + '"><img' + m[0] + 'src="' + m[1] + '?action=view'+ params + '"' + m[2] + '></a>'
        new_html = '<a href="' + m[1] + '?action=edit&parent=' + _wiki_parent + '">'
        new_html += '<img' + m[0] + 'src="' + m[1]
        new_html += '?action=view'+ params + '"' + m[2] + '></a>'
        return new_html

#href -- <a href="link">
def _wiki_href(content):
    """
    >>> _wiki_href('<a href="link">')
    '<a href="link?parent=">'
    """
    return re.sub(r'\<a(.*?)href\s*\=\s*\"([a-zA-Z0-9_\-\.]+)\"(.*?)\>',
                  _wiki_href_callback, content, flags=re.I)

def _wiki_href_callback(matchobj):
    global _wiki_parent
    m = matchobj.groups()
    return "<a%shref=\"%s?parent=%s\"%s>" % (m[0], m[1], _wiki_parent, m[2])


# http://pygments.org/docs/quickstart/
#code -- <code class="python">my code</code>
def _wiki_code(content):
    """
    >>> u = _wiki_code('<code class="python">my_code()</code>')
    >>> expected = '<div class="highlight"><pre><span class="n">my_code</span><span class="p">()</span>\\n</pre></div>\\n'
    >>> expected in u
    True

    """
    css_class = "python"
    if css_class:
        content = content.replace('<code>', '<code class=\"%s\">' % css_class);

    #syntax_css = u"<style>%s</style>" % HtmlFormatter().get_style_defs('.highlight')
    #content = syntax_css + content

    return re.sub(r'\<code\s+class\s*\=\s*\"([^\"]+)\"\>(.*?)\<\/code>',
                  _wiki_code_callback, content, flags=re.I | re.S)


def _wiki_code_callback(matchobj):
    m = matchobj.groups()
    content = m[1]
    content = re.sub(r'^\s*', '', content, re.S)
    content = re.sub(r'\s*$', '', content, re.S)
    # code_class = m[0]
    formatter = HtmlFormatter(noclasses=True)
    code = highlight(content, PythonLexer(), formatter)
    return code

def _wiki_pre_code_clean(pq_content):
    """ remove the double pre when <pre><code></code></pre>.

    For our tinymce rich text editor, we need to wrap code
    tags inside of pre tags. However, rendering them looks
    of silly because there is a pre wrapped in a pre.
    """
    if len(pq_content) == 1 and pq_content[0].tag == 'pre':
        if len(pq_content.find('div.highlight')):
            return pq(pq_content.find('div.highlight').outerHtml())

    for div in pq_content.find('pre div.highlight'):
        pq(div).parent().replace_with(pq(div))
    return pq_content

def _wiki_link(content):
    """
    #>>> _wiki_link('[[link#section]]')
    #'<a href="link?parent=">link</a>'
    """
    return re.sub('\[\[([^\]]+)\]\]', _wiki_link_callback, content)


def _wiki_link_callback(matchobj):
    global _wiki_parent
    m = matchobj.groups()

    parts = m[0].split("#")
    if parts and len(parts) == 2:
        link, section = parts
        section = '#' + section
    else:
        link = parts[0]
        section = ''

    name = link
    link = '/wiki/' + link
    if _wiki_parent:
        return f'<a href="{link}?parent={_wiki_parent}{section}">{name}</a>'
    else:
        return f'<a href="{link}{section}">{name}</a>'


def _wiki_quote(content, for_link_cb):
    '''
    >>> _wiki_quote('{{link#section}}')
    ''

    '''
    def quote_callback(m):
        return _wiki_quote_callback(m, for_link_cb)

    return re.sub('/\{\{([^\}]+)\}\}/', quote_callback, content)


def _wiki_quote_callback(m, for_link_cb):

    link, section = m[1].split("#")
    content = '' if for_link_cb is None else for_link_cb(link)
    content = pq(content).find('#' + section).outerHtml()

    return content if content else '{{' + f'{link}#{section}' + '}}'


def table_of_contents(pq_content):

    toc = pq('<nav id="toc" class="wiki-toc-nav"><ul class="nav"></ul></nav>')
    toc_ul = toc.find('ul.nav')
    found_a_heading = False
    previous_heading = None

    # for i, heading in enumerate(pq_content.find('h1,h2,h3,h4')):
    for i, heading in enumerate(pq_content.find('h1,h2,h3,h4')):
        title = pq(heading).text()
        header_link = (pq('<a title="Permalink to this definition">¶</a>')
            .addClass('header_link')
            .attr('href', '#' + title)
        )
        (pq(heading)
            .attr('id', title)
            .addClass('wiki-heading')
            .append(header_link))

        link = (pq('<a></a>')
            .text(title)
            .attr('href', '#' + title)
            .addClass('li' + heading.tag)
            .wrap('<li>'))

        if heading.tag in ['h1', 'h2']:
            previous_heading = heading
            previous_heading_link = link
            # link.addClass('active')
            toc_ul.append(link)
        elif heading.tag in ['h3', 'h4']:
            if previous_heading is not None and pq(previous_heading):
                ul_nav = pq(previous_heading_link).find('ul.nav:first')
                if not len(ul_nav):
                    ul_nav = pq('<ul class="nav"></ul>')
                    pq(previous_heading_link).append(ul_nav)
                ul_nav.append(link)
            else:
                toc_ul.append(link)
        found_a_heading = True
    if found_a_heading:
        return toc

def _wiki_section(content):
    """ Find all the sections (header tags), and make a table of contents.
    """
    if not content:
        return content

    pq_content = pq(content)
    toc = table_of_contents(pq_content)
    if toc is not None:
        pq_content.prepend(toc)
    return pq_content

def render_pq(content, for_link_cb=None, toc_separate=False):
    """ render the content, which is wiki markup.

    :param for_link_cb: takes a link and returns the wiki content for it.
    """
    if content is None or content is '':
        if toc_separate:
            return pq(None), pq(None)
        return pq(None)

    content = _wiki_quote(content, for_link_cb)
    content = _wiki_code(content)
    content = _wiki_href(content)
    content = _wiki_img(content)
    content = _wiki_link(content)

    pq_content = pq(content)
    pq_content = _wiki_pre_code_clean(pq_content)

    for anchor in pq_content.find('a'):
        pq(anchor).attr('rel', 'nofollow')
    for table in pq_content.find('table'):
        pq(table).addClass('table').wrap('<div class="table-responsive">')
    toc = table_of_contents(pq_content)

    if toc_separate:
        return pq_content, toc

    if toc is not None:
        pq_content.prepend(toc)
    return pq_content

def render(content, for_link_cb=None):
    """ render the content, which is wiki markup.

    :param for_link_cb: takes a link and returns the wiki content for it.
    """
    # if content is None or content is '':
    #     return ''
    if content is None or content is '':
        return ''
    return render_pq(content, for_link_cb).outerHtml()



if __name__ == "__main__":

    if "--test" in sys.argv:
        def _test():
            import doctest
            doctest.testmod()
        _test()
