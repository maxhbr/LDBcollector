from itertools import product
import logging
from pkg_resources import resource_exists, resource_string
import os.path
from pathlib import PurePath

from zope.interface import implementer

from pyramid.interfaces import IRendererFactory, IRenderer
from pyramid.asset import resolve_asset_spec
from pyramid.view import view_config

from scss import config as scss_config
from scss.namespace import Namespace
from scss.extension.api import Extension
from scss.extension.core import CoreExtension
from scss.extension.compass import CompassExtension
from scss.compiler import Compiler, SourceFile

logger = logging.getLogger('oscad_scss')

# Parts of the following code are adapted from the PyScss project
# (https://github.com/Kronuz/pyScss) which is
# Copyright (c) 2011, 2012 German M. Bravo (Kronuz)
# and is licensed under the MIT license. You can find a full copy of its
# license in the root of this project in the file LICENSE_PYSCSS

scss_config.STATIC_URL = ''


class AssetSpecOrigin(object):
    def __init__(self, pname, parts):
        self.pname = pname
        self.parts = parts

    @classmethod
    def from_assetspec(cls, assetspec):
        pname, basepath = resolve_asset_spec(assetspec)
        parts = os.path.split(basepath)
        return cls(pname=pname, parts=parts)

    def relative_to(self, relpath):
        return self.pname + ':' + \
                os.path.join(*(self.parts + os.path.split(relpath)[:-1]))

    def __truediv__(self, other):
        return AssetSpecOrigin(
            pname=self.pname,
            parts=self.parts + os.path.split(other),
        )

    def __str__(self):
        return self.pname + ':' + os.path.join(*self.parts)

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__,
            str(self),
        )


class CoreFunctions(Extension):
    name = 'core-functions'
    namespace = CoreExtension.namespace


class CompassFunctions(Extension):
    name = 'compass-functions'
    namespace = CompassExtension.namespace


class OscadScssExtension(Extension):
    name = 'oscad'
    namespace = Namespace()

    def __init__(self, asset_path):
        self.asset_path = asset_path

    def handle_import(self, name, compilation, rule):
        origin = rule.source_file.origin
        relpath = rule.source_file.relpath

        dirname, basename = os.path.split(name)

        search_path = []
        if isinstance(origin, AssetSpecOrigin):
            search_path.append(origin.relative_to(relpath))
        elif origin is not None:
            raise ValueError("Origin is invalid")
        search_path.extend(self.asset_path)

        for asset_location, prefix, suffix in product(
            search_path,
            ('_', ''),
            list(compilation.compiler.dynamic_extensions)
        ):

            filename = prefix + basename + suffix
            full_filename = os.path.join(
                asset_location, dirname, filename)

            pname, asset_filename = resolve_asset_spec(full_filename)
            if resource_exists(pname, asset_filename):
                content = resource_string(pname,
                                          asset_filename).decode('utf-8')
                return SourceFile(
                    origin=AssetSpecOrigin.from_assetspec(asset_location),
                    relpath=PurePath(dirname, filename),
                    contents=content,
                    encoding='utf-8',
                )


class OscadScssCompiler(object):
    def __init__(self, asset_path):
        self._compiler = Compiler(extensions=[OscadScssExtension(asset_path),
                                              CoreFunctions,
                                              CompassFunctions])

    def compile_from_path(self, filename, icon_font_path):
        return self._compiler.compile_string(
            '$icon-font-path: "{0}";\n'
            '@import "{1}"'.format(
                icon_font_path,
                filename))


@implementer(IRendererFactory, IRenderer)
class ScssRenderer(object):
    cache = None

    def __init__(self, info):
        self.cache = {}
        self.info = info
        asset_path = self.info.settings['scss.asset_path'].split()
        self.compiler = OscadScssCompiler(asset_path)

    def __call__(self, scss, system):
        request = system.get('request')
        response = request.response
        response.cache_control.max_age = 3600
        ct = response.content_type
        if ct == response.default_content_type:
            response.content_type = 'text/css'

        css = self.cache.get(request.url)

        if css is not None:
            return css

        dirname, filename = os.path.split(scss)
        css = self.compiler.compile_from_path(
                filename,
                request.static_path('bootstrap/fonts/'),
        )

        self.cache[request.url] = css
        return css


@view_config(route_name='scss', renderer='scss',
             request_method='GET')
def get_scss(root, request):
    return request.matchdict.get('css_path')
