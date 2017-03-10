import feedparser
def sanitize_html(html, force_https=True):
    """ santise_html(html) returns some sanitized html.
          It can be used to try and avoid basic html insertion attacks.

        >>> sanitize_html("<p>hello</p>")
        '<p>hello</p>'
        >>> sanitize_html("<script>alert('what')</script>")
        ''
    """
    clean_html = feedparser._sanitizeHTML(html, "utf-8", "text/html")
    if force_https:
        return clean_html.replace('src="http://', 'src="https://')
    else:
        return clean_html
