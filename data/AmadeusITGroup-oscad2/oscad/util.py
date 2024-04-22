from markupsafe import Markup
from pkg_resources import resource_isdir
from pyramid.exceptions import ConfigurationError

from .exceptions import UtilException
from .compat import urlparse


def _check_balances(text, begin, end):
    nesting = 0
    failed = False

    for char in text:
        if char == begin:
            nesting += 1
        elif char == end:
            if nesting == 0:
                failed = True
                break
            else:
                nesting -= 1
    if nesting != 0:
        failed = True

    if failed:
        raise UtilException('Unbalanced "{}{}" in "{}"'.format(
            begin, end, text))


def htmlize(text, tag='b', begin='{', end='}'):
    escaped = Markup.escape(text)
    _check_balances(text, begin, end)
    begin_tag = Markup('<{tag}>').format(tag=tag)
    end_tag = Markup('</{tag}>').format(tag=tag)

    return escaped.replace(begin, begin_tag).replace(end, end_tag)


def strip_if_empty(text):
    if text.isspace():
        return ''
    return text


def load_themes(config, settings):
    for theme in settings.get('themes', '').split():
        config.override_asset('oscad:templates/', '%s:templates/' % theme)
        config.override_asset('oscad:static/', '%s:static/' % theme)
        config.override_asset('oscad:assets/', '%s:assets/' % theme)

        if resource_isdir(theme, 'locale'):
            config.add_translation_dirs('%s:locale' % theme)

        try:
            config.include(theme)
        except ConfigurationError:
            pass


def is_application_url(request, url):
    p = urlparse(url)

    if p.scheme and p.scheme != request.scheme:
        return False

    if p.netloc and p.netloc != request.host:
        return False

    if not p.path:
        return False

    return is_url_prefix(request.script_name, p.path)


def is_url_prefix(prefix, url):
    if not url.startswith(prefix):
        return False

    if prefix and prefix[-1] != '/' and \
       len(url) > len(prefix) and url[len(prefix)] != '/':
        return False

    return True
