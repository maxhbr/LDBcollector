from datetime import timedelta

from babel import Locale
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther, HTTPNotFound
from pyramid.response import Response
from pkg_resources import resource_stream

import oscad_data as data

from . import exceptions
from .models import OSUC, LSUC
from .version import __version__ as oscad_version

PLANNED_LICENSES = sorted(['CDDL-1.0', 'ZLIB'])
DEFAULT_LICENSE = 'GPLv2.0'


def translation_texts_for_osuc(request, osuc):
    _ = request.translate

    if osuc.type == 'proapse':
        type_ = _('application')
    elif osuc.type == 'snimoli':
        type_ = _('library')

    if osuc.recipient == '4yourself':
        recipient = _('use')
    elif osuc.recipient == '2others':
        recipient = _('distribute')

    if osuc.state == 'unmodified':
        state_article = _('an')
        state = _('unmodified')
    elif osuc.state == 'modified':
        state_article = _('a')
        state = _('modified')

    if osuc.form == 'sources':
        form = _('sources')
    elif osuc.form == 'binaries':
        form = _('binary files')
    elif osuc.form == 'any':
        form = _('sources or binary files')

    if osuc.context == 'independent':
        context = _('independent')
        context_suffix = _('piece of software')
    elif osuc.context == 'embedded':
        context = _('embedded')
        context_suffix = _('in my own software development')

    return {
        'type_': type_,
        'state_article': state_article,
        'state': state,
        'form': form,
        'context_': context,
        'context_suffix': context_suffix,
        'recipient': recipient,
    }


def extract_params(request, params):
    try:
        return [request.params[p] for p in params]
    except KeyError as e:
        raise exceptions.MissingParameter(e.args[0])


def reset(request):
    return HTTPSeeOther(request.referer or request.application_url)


def show_error(request, message):
    print(request.wants_json)
    if request.wants_json:
        return {
            'ok': False,
            'message': message,
        }
    else:
        request.session.flash(message)
        return reset(request)


@view_config(route_name='index')
def index(request):
    return HTTPSeeOther(request.route_path('request'))


@view_config(route_name='request', renderer='templates/oscad/request.jinja2',
             request_method='GET')
def request(request):
    return {
        'licenses': data.valid_licenses,
        'license_details': data.license_details,
        'default_license': DEFAULT_LICENSE,
        'planned_licenses': PLANNED_LICENSES,
    }


@view_config(route_name='imprint', renderer='templates/oscad/imprint.jinja2')
def imprint(request):
    return {}


@view_config(route_name='about', renderer='templates/oscad/about.jinja2')
def about(request):
    return {
        'oscad_version': oscad_version,
    }


@view_config(route_name='license', renderer='templates/oscad/license.jinja2')
def license(request):
    slug = request.matchdict['license']
    info = data.license_details[slug]
    name = info['name']
    text = info['text']

    return {
        'slug': slug,
        'name': name,
        'text': text,
    }


@view_config(route_name='components',
             renderer='templates/oscad/components.jinja2')
def components(request):
    avail = request.available_locales

    def display_name(tag):
        return Locale(tag).get_display_name(request.locale_name)

    return {
        'langs': [(l, display_name(l)) for l in avail if l != 'en']
    }


@view_config(route_name='change_language')
def change_language(request):
    lang = request.matchdict.get('lang')
    resp = HTTPSeeOther(request.application_url)

    if lang is None:
        resp.unset_cookie('_LOCALE_')
    else:
        # max_age = year
        resp.set_cookie('_LOCALE_', lang, max_age=timedelta(days=365))

    return resp


@view_config(route_name='lsuc', renderer='templates/oscad/result.jinja2')
def lsuc(request):
    lsuc = LSUC.from_name(request.matchdict.get('lsuc'))
    osuc = OSUC.from_number(request.matchdict.get('osuc'))

    if lsuc is None or osuc is None:
        return HTTPNotFound()

    lsuc_extra_info_hook = request.oscad_settings.lsuc_extra_info

    if lsuc_extra_info_hook:
        lsuc_extra_info = lsuc_extra_info_hook(request, lsuc, osuc)
    else:
        lsuc_extra_info = None

    result = {
        'osuc': osuc,
        'lsuc': lsuc,
        'lsuc_extra_info': lsuc_extra_info,
    }

    result.update(translation_texts_for_osuc(request, osuc))

    return result


@view_config(route_name='result')
def result(request):

    license, = extract_params(request, ['license'])

    if 'osuc' in request.params:
        osuc_number, = extract_params(request, ['osuc'])
        osuc = OSUC.from_number(osuc_number)

    else:
        recipient, type_, state, form, context = extract_params(
            request,
            ['recipient', 'type', 'state', 'form', 'context']
        )

        osuc = OSUC.from_attrs(recipient=recipient, type=type_, state=state,
                               form=form, context=context)

    if osuc is None:
        raise exceptions.InvalidParameterCombination()

    lsuc = osuc.get_lsuc(license)

    if lsuc is None:
        raise exceptions.InvalidParameterCombination()

    return HTTPSeeOther(request.route_path('lsuc',
                                           lsuc=lsuc.mnemonic,
                                           osuc=osuc.number))


@view_config(route_name='matrix_request',
             renderer='templates/oscad/matrix.jinja2')
def matrix_request(request):
    return {
        'table': data.license_matrix(),
        'licenses': data.valid_licenses,
        'license_details': data.license_details,
        'default_license': DEFAULT_LICENSE,
        'planned_licenses': PLANNED_LICENSES,
    }


@view_config(route_name='help', renderer='templates/oscad/help.jinja2')
def help(request):
    return {}


@view_config(route_name='translation_file')
def translation_file(request):
    lang = request.matchdict['lang']

    if lang not in request.available_locales:
        return HTTPNotFound()

    gettext_file = 'locale/{0}/LC_MESSAGES/oscad.po'.format(lang)

    try:
        file_stream = resource_stream('oscad', gettext_file)
    except IOError:
        return HTTPNotFound()

    resp = Response()

    resp.content_disposition = 'attachment; filename=oscad-{0}.po'.format(lang)
    resp.app_iter = file_stream
    resp.content_type = 'application/x-gettext'

    return resp


@view_config(route_name='translation_template')
def translation_template(request):
    resp = Response()
    resp.content_disposition = 'attachment; filename=oscad.pot'
    resp.app_iter = resource_stream('oscad', 'locale/oscad.pot')
    # otherwise Firefox thinks its a PowerPoint
    resp.content_type = 'text/plain'
    return resp


@view_config(context=exceptions.MissingParameter, renderer='')
def missing_parameter(exc, request):
    return show_error(
        request,
        request.translate('Missing parameter: %(param)s', param=exc.param))


@view_config(context=exceptions.InvalidParameterCombination)
def invalid_parameters(exc, request):
    return show_error(
        request,
        request.translate('The combination of parameters you have entered is'
                          ' invalid'))


@view_config(context=exceptions.InvalidLicense)
def invalid_license(exc, request):
    return show_error(
        request,
        request.translate('The license "%(license)s" you have entered is not'
                          ' covered by this application', license=exc.license))


def export(request):
    from pyramid.response import Response
    from pyramid.httpexceptions import HTTPServerError
    from subprocess import Popen, PIPE
    import os.path
    import datetime

    response = Response(
        content_type='application/zip',
    )

    if not os.path.isdir('.git'):
        raise HTTPServerError('not a git directory')

    try:
        proc = Popen(
            [
                'git',
                'describe',
                '--always',
            ],
            stdout=PIPE)

        rev = proc.stdout.read().strip()

        proc = Popen(
            [
                'git',
                'archive',
                '--format=zip',
                '--prefix=oscad/',
                '-9',
                'HEAD',
            ],
            stdout=PIPE)
    except OSError as e:
        raise HTTPServerError(e)

    time = datetime.datetime.now().replace(microsecond=0)

    filename = 'oscad-{}-git-{}.zip'.format(
        time.isoformat(),
        rev
    )

    response.content_disposition = 'attachment; filename="{}"'.format(filename)
    response.body_file = proc.stdout

    return response
