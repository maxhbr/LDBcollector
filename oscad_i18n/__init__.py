import os.path

from pyramid.i18n import negotiate_locale_name
from pyramid.interfaces import (
    ILocalizer,
    ITranslationDirectories,
    )
from babel.core import Locale
from babel.support import Translations, Format
from zope.interface import Interface

# Parts of the following code are adapted from the Babel project
# (http://babel.pocoo.org/) which is
# Copyright (C) 2013 by the Babel Team, see its respective AUTHORS for more
# information,
# and is licensed under the BSD license. You can find a full copy of its
# license in the root of this project in the file LICENSE_BABEL


class ITranslationDomain(Interface):
    pass


class Localizer(object):
    def __init__(self, locale, translations):
        self.locale = locale
        self._translations = translations
        self.format = Format(locale)

    def gettext(self, string, **variables):
        if variables:
            return self._translations.ugettext(string) % variables
        return self._translations.ugettext(string)

    def ngettext(self, singular, plural, num, **variables):
        if variables:
            return self._translations.ungettext(
                singular, plural, num) % variables
        return self._translations.ungettext(singular, plural, num)

    def pgettext(self, context, string, **variables):
        if variables:
            return self._translations.upgettext(context, string) % variables
        return self._translations.upgettext(context, string)

    def npgettext(self, context, singular, plural, num, **variables):
        if variables:
            return self._translations.unpgettext(
                context, singular, plural, num) % variables
        return self._translations.unpgettext(context, singular, plural, num)

    pluralize = ngettext
    translate = gettext


def make_localizer(current_locale_name, translation_directories, domain=None):
    """ Create a :class:`pyramid.i18n.Localizer` object
    corresponding to the provided locale name from the
    translations found in the list of translation directories."""

    locale = Locale.parse(current_locale_name)

    translations = Translations(domain=domain)
    translations._catalog = {}

    locales_to_try = []
    if not current_locale_name == locale.language:
        locales_to_try.append(locale.language)
    locales_to_try.append(current_locale_name)

    # intent: order locales left to right in least specific to most specific,
    # e.g. ['de', 'de_DE'].  This services the intent of creating a
    # translations object that returns a "more specific" translation for a
    # region, but will fall back to a "less specific" translation for the
    # locale if necessary.  Ordering from least specific to most specific
    # allows us to call translations.add in the below loop to get this
    # behavior.

    for tdir in translation_directories:
        locale_dirs = []
        for lname in locales_to_try:
            ldir = os.path.realpath(os.path.join(tdir, lname))
            if os.path.isdir(ldir):
                locale_dirs.append(ldir)

        for locale_dir in locale_dirs:
            messages_dir = os.path.join(locale_dir, 'LC_MESSAGES')
            if not os.path.isdir(os.path.realpath(messages_dir)):
                continue
            for mofile in os.listdir(messages_dir):
                mopath = os.path.realpath(os.path.join(messages_dir,
                                                       mofile))
                if mofile.endswith('.mo') and os.path.isfile(mopath):
                    with open(mopath, 'rb') as mofp:
                        domain = mofile[:-3]
                        dtrans = Translations(mofp, domain)
                        translations.add(dtrans)

    return Localizer(locale=locale, translations=translations)


def locale_name(request):
    locale_name = negotiate_locale_name(request)
    return locale_name


def localizer(request):
    registry = request.registry

    current_locale_name = request.locale_name
    localizer = registry.queryUtility(ILocalizer, name=current_locale_name)

    if localizer is None:
        # no localizer utility registered yet
        tdirs = registry.queryUtility(ITranslationDirectories, default=[])
        domain = registry.queryUtility(ITranslationDomain, default=None)
        localizer = make_localizer(current_locale_name, tdirs, domain)

        registry.registerUtility(localizer, ILocalizer,
                                 name=current_locale_name)
        request.localizer = localizer

    return localizer


def translate(request, *args, **kwargs):
    return request.localizer.translate(*args, **kwargs)


def add_renderer_globals(event):
    request = event['request']
    localizer = request.localizer
    event['localizer'] = localizer
    event['available_locale_names'] = request.available_locales

    event['gettext'] = localizer.gettext
    event['_'] = localizer.gettext
    event['ngettext'] = localizer.ngettext
    event['pgettext'] = localizer.pgettext
    event['npgettext'] = localizer.npgettext


def add_available_locales(event):
    request = event.request
    settings = request.registry.settings

    request.available_locales = settings['available_locales']


def set_default_domain(config, domain):
    def callback():
        registry = config.registry
        registry.registerUtility(domain, ITranslationDomain)
    discriminator = ('set_default_domain',)
    config.action(discriminator, callable=callback)


def includeme(config):
    config.add_directive('set_default_i18n_domain', set_default_domain)

    config.add_request_method(locale_name, reify=True)
    config.add_request_method(localizer, reify=True)
    config.add_request_method(translate)

    config.add_subscriber('.add_renderer_globals',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('.add_available_locales',
                          'pyramid.events.NewRequest')

    default_domain = config.registry.settings.get('i18n.default_domain')
    if default_domain:
        config.set_default_i18n_domain(default_domain)
