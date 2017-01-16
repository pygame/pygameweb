"""Wiki related code.

This works with basic html as the markup format as found on pygame.org


There are still a few items that need to be ported so all existing
content in the wiki will work ok. This involves giving the wiki rendering
code db access to look up other wiki content.

Note, that the output of this needs to be run through html sanitizers.
"""

import sys
import re

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
    return highlight(content, PythonLexer(), HtmlFormatter())


#link -- [[link#section]]
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
    else:
        link = parts[0]
        section = ""

    #$e = $db->query1("select id,name from wiki where".
    #    " link = ".$db->sqlstring($link)." and latest = 1 limit 1");
    #if (!$e["id"]) {
    #        $e["name"] = $link;
    #}
    name = link
    link = "//pygame.org/wiki/" + link
    return "<a href=\"{link}?parent={_wiki_parent}\">{name}</a>".format(link=link,
                                                                        _wiki_parent=_wiki_parent,
                                                                        name=name)






if 0:

    from pyquery import PyQuery as pq

    # TODO: untested quote stuff.
    import MySQLdb
    from generate_json import sanitise_the_rows

    #quote -- {{link#section}}
    def _wiki_quote(content):
        '''
        >>> _wiki_quote('{{link#section}}')
        ''

        '''

        return re.sub('/\{\{([^\}]+)\}\}/', _wiki_quote_callback, content)


    def _wiki_content_for_link(link):
        ''' returns the wiki content for the given link.
        '''
        # $e = $db->query1("select id,content from wiki where".
        #     " link = ".$db->sqlstring($link)." and latest = 1 limit 1");
        # $content = $e["content"];

        #TODO: actually link here.
        return 'The link content.'

        db = MySQLdb.connect(host="localhost",
                         user="pygame",
                         passwd="password",
                         db=self.dbname,
                         use_unicode = True)


    def _wiki_getsection(content, section):
        ''' within the content search for the section
        '''
        return pq(content).find('#' + section).outerHtml()


    def _wiki_quote_callback(m):
    #    global $db;

        link, section = m[1].split("#")

        content = _wiki_content_for_link(link)
        content = _wiki_getsection(content, section)

        if content:
            return content

        link = "{link}#{section}".format(link=link,
                                         section=section)
        return '{{' + link + '}}'






def render(content):

    #$content = $e["content"];
    #$content = _wiki_quote($content);
    #$content = _wiki_code($content);
    #$content = _wiki_href($content);
    #$content = _wiki_img($content);
    #$content = _wiki_link($content);
    #$content = _wiki_section($content);

    #content = _wiki_quote(content)
    content = _wiki_code(content)
    content = _wiki_href(content)
    content = _wiki_img(content)
    content = _wiki_link(content)
    #content = _wiki_section(content)
    return content



if __name__ == "__main__":


    if "--test" in sys.argv:
        def _test():
            import doctest
            doctest.testmod()
        _test()
