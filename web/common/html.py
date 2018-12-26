from lxml.html.clean import clean_html


def sanitize(html_string):
    return clean_html(html_string)
