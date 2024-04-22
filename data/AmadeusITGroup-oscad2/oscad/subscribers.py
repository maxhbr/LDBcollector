from pyramid.i18n import default_locale_negotiator
from pkg_resources import resource_exists


import logging
import markupsafe

logger = logging.getLogger('oscad')


def add_renderer_globals(event):
    request = event['request']
    event['Markup'] = markupsafe.Markup

    toplevel_links = [
        (request.route_path('request'), request.translate('New Request')),
        (request.route_path('matrix_request'),
         request.translate('Matrix Request')),
        (request.route_path('about'), request.translate('About')),
        (request.route_path('components'), request.translate('Components')),
        (request.route_path('help'), request.translate('Help')),
    ]

    # FIXME get template name from actual route/view
    if resource_exists('oscad', 'templates/oscad/imprint.jinja2'):
        toplevel_links.insert(-1,
                              (request.route_path('imprint'),
                               request.translate('Imprint')))

    event['toplevel_links'] = toplevel_links


def locale_negotiator(request):
    locale_name = default_locale_negotiator(request)
    if locale_name is None:
        accept_language = request.accept_language

        # Header is set, if not the first offer is returned
        # We want to use the configured default
        if accept_language:
            locale_name = accept_language.best_match(
                request.available_locales,
            )

    return locale_name


def jsonify(event):
    def has_ext(string, ext):
        return string.endswith('.' + ext)

    def strip_ext(string, ext):
        if has_ext(string, ext):
            return string[:-(len(ext) + 1)]

    JSON = 'application/json'
    HTML = 'text/html'

    wants_json = False
    request = event.request

    if request.accept.best_match([HTML, JSON], HTML) == JSON:
        wants_json = True

    if has_ext(request.path_info, 'json'):
        wants_json = True
        request.path_info = strip_ext(request.path_info, 'json')

    if wants_json:
        request.override_renderer = 'json'
    request.wants_json = wants_json
