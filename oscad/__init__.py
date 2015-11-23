from collections import namedtuple

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.settings import asbool

import jinja2

from .subscribers import locale_negotiator
from .util import load_themes, htmlize
from ._scss import renderer_factory
from . import version

__version__ = version.__version__


class OscadSettings(object):
    def __init__(self, legal_expert=None, lsuc_extra_info=None,
                 oslic_url=None):
        self.legal_expert = legal_expert
        self.lsuc_extra_info = lsuc_extra_info
        self.oslic_url = oslic_url


Piwik = namedtuple('Piwik', ['baseurl', 'siteid'])


def oscad_default_legal_expert(request):
    return request.translate('your legal expert')

oslic_url = 'http://opensource.telekom.net/oslic/releases/oslic-1.0.0.pdf'

oscad_default_settings = OscadSettings(legal_expert=oscad_default_legal_expert,
                                       lsuc_extra_info=None,
                                       oslic_url=oslic_url)


def piwik_from_settings(settings):
    baseurl = settings.get('piwik.baseurl')
    siteid = settings.get('piwik.siteid')

    if baseurl and siteid is not None:
        return Piwik(baseurl, siteid)
    return None


def oscad_settings(request):
    return request.registry.settings.oscad_settings


def piwik(request):
    return request.registry.settings.piwik


def add_toplevel_link(config, route_name, link_text):
    def callback():
        registry = config.registry
        if not hasattr(registry, 'toplevel_links'):
            registry.toplevel_links = []
        registry.toplevel_links.append((route_name, link_text))
    discriminator = ('add_toplevel_link',)
    config.action(discriminator, callable=callback)


def set_toplevel_links(config, links):
    def callback():
        registry = config.registry
        registry.toplevel_links = links
    discriminator = ('set_toplevel_links',)
    config.action(discriminator, callable=callback)


def scss_path(request, name, **kwargs):
    return request.route_path('scss', css_path=name, **kwargs)


def oslic_chapter_url(request, location):
    """
    Take a location string like "1.2.3" or "1" and returns the url to link to
    this chapter in the configured version on OSLiC
    """
    oslic_url = request.oscad_settings.oslic_url

    level = location.count('.')

    if level == 0:
        level_name = 'chapter'
    else:
        level_name = ('sub' * (level - 1)) + 'section'

    # we could also add #nameddest=section1.1.1
    return oslic_url + '#' + level_name + '.' + location


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['available_locales'] = settings.get(
        'available_locales', '').split()
    static_prefix = settings.get('static_prefix', 'static')

    config = Configurator(settings=settings)

    config.include('pyramid_jinja2')
    config.add_jinja2_search_path('oscad:templates')

    config.include('oscad_i18n')
    config.set_default_i18n_domain('oscad')

    config.add_directive('set_toplevel_links', set_toplevel_links)
    config.add_directive('add_toplevel_link', add_toplevel_link)
    config.add_request_method(scss_path)
    config.add_request_method(oscad_settings, property=True)
    config.add_request_method(piwik, property=True)
    config.add_request_method(oslic_chapter_url)

    config.add_renderer('scss', renderer_factory)

    config.set_locale_negotiator(locale_negotiator)
    config.set_session_factory(UnencryptedCookieSessionFactoryConfig(''))
    config.add_subscriber('oscad.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('oscad.subscribers.jsonify',
                          'pyramid.events.NewRequest')
    config.add_translation_dirs('oscad:locale')

    config.add_route('scss', static_prefix + '/css/{css_path:.*}.css')
    config.add_static_view(static_prefix, 'static', cache_max_age=3600)

    config.add_static_view(
        settings.get('bootstrap_location', static_prefix + '/bootstrap'),
        'bootstrap')
    config.add_static_view(
        settings.get('jquery_location', static_prefix + '/jquery'),
        'jquery')

    config.registry.settings.oscad_settings = oscad_default_settings
    config.registry.settings.piwik = piwik_from_settings(settings)

    config.add_route('index', '')
    config.add_route('request', 'request')
    config.add_route('matrix_request', 'matrix')
    config.add_route('result', 'result')
    config.add_route('lsuc', 'result/{osuc}/{lsuc}')
    config.add_route('imprint', 'imprint')
    config.add_route('about', 'about')
    config.add_route('help', 'help')
    config.add_route('components', 'components')
    config.add_route('license', 'license/{license}')
    config.add_route('change_language', 'language/{lang}')
    config.add_route('translation_template', 'translations/oscad.pot')
    config.add_route('translation_file', 'translations/{lang}')

    if asbool(settings.get('allow_export')):
        config.add_view('export', 'views:export')
        config.add_route('export', 'export')

    load_themes(config, settings)

    config.scan()
    config.commit()

    jenv = config.get_jinja2_environment()
    jenv.filters['htmlize'] = htmlize
    jenv.undefined = jinja2.StrictUndefined

    return config.make_wsgi_app()
