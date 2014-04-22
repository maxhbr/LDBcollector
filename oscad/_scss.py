import logging
from pkg_resources import resource_exists, resource_string
import os.path

from zope.interface import implementer
from itertools import product

from pyramid.interfaces import ITemplateRenderer
from pyramid.asset import resolve_asset_spec
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from scss import Scss, SourceFile, dequote, SassRule, config as scss_config
from scss.errors import SassError

Logger = logging.getLogger('oscad_scss')
scss_config.STATIC_URL = ''

# Parts of the following code are adapted from the PyScss project
# (https://github.com/Kronuz/pyScss) which is
# Copyright (c) 2011, 2012 German M. Bravo (Kronuz)
# and is licensed under the MIT license. You can find a full copy of its
# license in the root of this project in the file LICENSE_PYSCSS


class ScssNotFound(Exception):
    pass


class OscadScss(Scss):
    def Compilation(self, scss_string=None, scss_file=None,
                    super_selector=None, filename=None, is_sass=None,
                    line_numbers=True, source_file=None):
        if super_selector:
            self.super_selector = super_selector + ' '
        self.reset()

        if scss_string is not None:
            source_file = SourceFile.from_string(scss_string, filename, is_sass, line_numbers)
        elif scss_file is not None:
            source_file = SourceFile.from_filename(scss_file, filename, is_sass, line_numbers)

        if source_file is not None:
            # Clear the existing list of files
            self.source_files = []
            self.source_file_index = dict()

            self.source_files.append(source_file)
            self.source_file_index[source_file.filename] = source_file

        # this will compile and manage rule: child objects inside of a node
        self.parse_children()

        # this will manage @extends
        self.apply_extends()

        rules_by_file, css_files = self.parse_properties()

        all_rules = 0
        all_selectors = 0
        exceeded = ''
        final_cont = ''
        files = len(css_files)
        for source_file in css_files:
            rules = rules_by_file[source_file]
            fcont, total_rules, total_selectors = self.create_css(rules)
            all_rules += total_rules
            all_selectors += total_selectors
            if files > 1 and self.scss_opts.get('debug_info', False):
                if source_file.is_string:
                    final_cont += "/* %s %s generated add up to a total of %s %s accumulated%s */\n" % (
                        total_selectors,
                        'selector' if total_selectors == 1 else 'selectors',
                        all_selectors,
                        'selector' if all_selectors == 1 else 'selectors',
                        exceeded)
                else:
                    final_cont += "/* %s %s generated from '%s' add up to a total of %s %s accumulated%s */\n" % (
                        total_selectors,
                        'selector' if total_selectors == 1 else 'selectors',
                        source_file.filename,
                        all_selectors,
                        'selector' if all_selectors == 1 else 'selectors',
                        exceeded)
            final_cont += fcont

        return final_cont

    def _load_file(self, rule, name):

        name, ext = os.path.splitext(name)
        if ext:
            search_exts = [ext]
        else:
            search_exts = ['.scss', '.sass']

        dirname, name = os.path.split(name)

        seen_paths = []


        # search_path is an assetspec
        # relpath is relative to the parent
        # dirname is from the import statement
        # name is the file itself

        for search_path in self.search_paths:
            for relpath in [rule.source_file.parent_dir]:
            # for basepath in [rule.source_file.parent_dir]:

                full_path = os.path.join(search_path, relpath, dirname)

                if full_path in seen_paths:
                    continue
                seen_paths.append(full_path)

                for prefix, suffix in product(('_', ''), search_exts):
                    full_filename = os.path.join(
                        full_path, prefix + name + suffix)

                    pname, filename = resolve_asset_spec(full_filename)
                    if resource_exists(pname, filename):
                        content = resource_string(pname,
                                                  filename).decode('utf-8')
                        return (filename,
                                os.path.join(relpath, dirname),
                                content,
                                seen_paths)

        return None, None, None, seen_paths

    def _do_import(self, rule, scope, block):
        """
        Implements @import
        Load and import mixins and functions and rules
        """
        # Protect against going to prohibited places...
        if any(scary_token in block.argument for
               scary_token in ('..', '://', 'url(')):
            rule.properties.append((block.prop, None))
            return

        names = block.argument.split(',')
        for name in names:
            name = dequote(name.strip())

            full_name, relpath, content, seen_paths = self._load_file(rule, name)

            if full_name is None:
                load_paths_msg =\
                    "\nLoad paths:\n\t%s" % "\n\t".join(seen_paths)
                raise ScssNotFound(
                    "File to import not found or unreadable: '%s' (%s)%s",
                    name, rule.file_and_line, load_paths_msg)

            source_file = SourceFile(full_name,
                                     content)
            source_file.parent_dir = relpath

            import_key = (name, source_file.parent_dir)
            if rule.namespace.has_import(import_key):
                # If already imported in this scope, skip
                continue

            _rule = SassRule(
                source_file=source_file,
                lineno=block.lineno,
                import_key=import_key,
                unparsed_contents=source_file.contents,

                # rule
                options=rule.options,
                properties=rule.properties,
                extends_selectors=rule.extends_selectors,
                ancestry=rule.ancestry,
                namespace=rule.namespace,
            )
            rule.namespace.add_import(import_key,
                                      rule.import_key, rule.file_and_line)
            self.manage_children(_rule, scope)


def renderer_factory(info):
    return ScssRenderer(info, {})


@implementer(ITemplateRenderer)
class ScssRenderer(object):
    cache = None

    def __init__(self, info, options):
        self.cache = {}
        self.info = info
        self.options = options

    def __call__(self, scss, system):
        request = system.get('request')
        response = request.response
        response.cache_control.max_age = 3600
        ct = response.content_type
        if ct == response.default_content_type:
            response.content_type = 'text/css'

        asset_path = self.info.settings['scss.asset_path'].split()
        parser = OscadScss(scss_opts=self.options,
                           search_paths=asset_path)

        dirname, filename = os.path.split(scss)
        try:
            source_file = SourceFile('split',
                                     '$icon-font-path: "{0}";\n'
                                     '@import "{1}"'.format(
                                         request.static_path('bootstrap/fonts/'),
                                         filename))
            source_file.parent_dir = dirname
            css = parser.compile(source_file=source_file)
        except SassError as e:
            raise HTTPNotFound(e)
        return css


@view_config(route_name='scss', renderer='scss',
             request_method='GET')
def get_scss(root, request):
    return request.matchdict.get('css_path')
