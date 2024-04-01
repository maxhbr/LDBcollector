#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse
import logging
import sys
import traceback
import re

from flame.license_db import FossLicenses
from flame.license_db import Validation
import flame.config
from flame.format import OUTPUT_FORMATS
from flame.format import OutputFormatterFactory
from flame.exception import FlameException

def get_parser():

    parser = argparse.ArgumentParser(
        description=flame.config.DESCRIPTION,
        epilog=flame.config.EPILOG,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument('-fc', '--flame-config',
                        type=str,
                        dest='flame_config',
                        help='Read settings from configuration file.',
                        default=None)

    parser.add_argument('-ld', '--license-dir',
                        type=str,
                        dest='license_dir',
                        help='Instead of using flame\'s built in licenses, use the licenses in the supplied directory',
                        default=None)

    parser.add_argument('-ald', '--additional-license-dir',
                        type=str,
                        dest='additional_license_dir',
                        help='Add licenses as found in the supplied directory',
                        default=None)

    parser.add_argument('-lmf', '--license-matrix-file',
                        type=str,
                        dest='license_matrix_file',
                        help='Supply license matrix to override OSADL\'s license compatibility matrix',
                        default=None)

    parser.add_argument('-ndu', '--no-dual-update',
                        action='store_true',
                        help='do not update dual licenses (e.g. GPL-2.0-or-later -> GPL-2.0-only OR GPL-3.0-only)',
                        default=False)

    parser.add_argument('-of', '--output-format',
                        type=str,
                        help=f'Chose output format. Available formats: {", ".join(OUTPUT_FORMATS)}',
                        default='text')

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='output verbose information',
                        default=False)

    parser.add_argument('-V', '--version',
                        action='store_true',
                        help='output version information',
                        default=False)

    parser.set_defaults(which='help', func=version_info)

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='output debug information to stderr',
                        default=False)

    parser.add_argument('-c', '--check',
                        action='store_true',
                        help='check all license files against JSON schema when initializing. Mainly for the flame developers.',
                        default=False)

    subparsers = parser.add_subparsers(help='Sub commands')
    parser.add_argument('--validate-spdx', action='store_true', dest='validate_spdx', help='Validate that the resulting license expression is valid according to SPDX syntax', default=False)
    parser.add_argument('--validate-relaxed', action='store_true', dest='validate_relaxed', help='Validate that the resulting license expression is valid according to SPDX syntax, but allow non SPDX identifiers ', default=False)
    parser.add_argument('--validate-osadl', action='store_true', dest='validate_osadl', help='Validate that the resulting licenses are supported by OSADL\'s compatibility matrix.', default=False)

    # license
    parser_e = subparsers.add_parser(
        'license', help='Convert license to SPDX identifiers and syntax')
    parser_e.set_defaults(which='license', func=show_license)
    parser_e.add_argument('license', type=str, nargs='+', help='license expression to fix')

    # full license
    parser_e = subparsers.add_parser(
        'license-full', help='Display full information about the license')
    parser_e.set_defaults(which='license-full', func=full_license)
    parser_e.add_argument('license', type=str, help='license to display fully. Only single license is allowed')

    # compatibility
    parser_c = subparsers.add_parser(
        'compat', help='Convert license to using licenses existing in the OSADL\'s matrix')
    parser_c.set_defaults(which='compat', func=compatibility)
    parser_c.add_argument('license', type=str, nargs='+', help='license name to display')

    # simplify
    parser_s = subparsers.add_parser(
        'simplify', help='Simplify a license (SPDX syntax) expression, e.g. "MIT AND MIT" -> "MIT"')
    parser_s.set_defaults(which='simplify', func=simplify)
    parser_s.add_argument('license_expression', type=str, nargs='+', help='license expression to simplify')

    # aliases
    parser_a = subparsers.add_parser(
        'aliases', help='Display all aliases')
    parser_a.set_defaults(which='aliases', func=aliases)
    parser_a.add_argument('--license', '-l', type=str, dest='alias_license', help='List only the aliases for licenses containing the given string', default=None)

    # compatbilities
    parser_cs = subparsers.add_parser(
        'compats', help='Display all compatibilities')
    parser_cs.set_defaults(which='compats', func=compats)

    # operators
    parser_os = subparsers.add_parser(
        'operators', help='Display all operators')
    parser_os.set_defaults(which='operators', func=operators)

    # licenses
    parser_cs = subparsers.add_parser(
        'licenses', help='show all licenses')
    parser_cs.set_defaults(which='licenses', func=licenses)

    # unknown
    parser_u = subparsers.add_parser(
        'unknown', help='Show the unknown licenses for a license expression. Intended for foss-licenses developers.')
    parser_u.set_defaults(which='unknown', func=unknown)
    parser_u.add_argument('license', type=str, nargs='+', help='license expression to fix')

    return parser

def parse():

    return get_parser().parse_args()

def operators(fl, formatter, args):
    all_op = fl.operators()
    return formatter.format_operators(all_op, args.verbose)

def aliases(fl, formatter, args):
    all_aliases = fl.alias_list(args.alias_license)
    return formatter.format_alias_list(all_aliases, args.verbose)

def licenses(fl, formatter, args):
    all_licenses = fl.licenses()
    return formatter.format_licenses(all_licenses, args.verbose)

def unknown(fl, formatter, args):
    validations = __validations(args)
    compat_license_expression = fl.expression_license(' '.join(args.license), validations=validations, update_dual=(not args.no_dual_update))
    compat_licenses = [x.strip() for x in re.split('\(|OR|AND|\)', compat_license_expression['identified_license'])]
    compat_licenses = [x for x in compat_licenses if x]
    unknown_symbols = set()
    for compat_license in compat_licenses:
        if compat_license not in fl.known_symbols():
            unknown_symbols.add(compat_license)
    if len(unknown_symbols) != 0:
        raise FlameException('Unknown symbols identified.\n' + '\n'.join(list(unknown_symbols)))
    return 'OK', None

def simplify(fl, formatter, args):
    simplified = fl.simplify(args.license_expression)
    return str(simplified) # formatter.format_licenses(all_licenses, args.verbose)

def compats(fl, formatter, args):
    all_compats = fl.compatibility_as_list()
    return formatter.format_compat_list(all_compats, args.verbose)

def version_info(fl, formatter, args):
    return flame.config.SW_VERSION, None

def compatibility(fl, formatter, args):
    validations = __validations(args)
    compatibilities = fl.expression_compatibility_as(' '.join(args.license), validations)
    return formatter.format_compatibilities(compatibilities, args.verbose)

def show_license(fl, formatter, args):
    validations = __validations(args)
    expression = fl.expression_license(' '.join(args.license), validations=validations, update_dual=(not args.no_dual_update))
    return formatter.format_expression(expression, args.verbose)

def full_license(fl, formatter, args):
    expr_split = fl.expression_license(args.license)['identified_license'].split()

    if len(expr_split) == 1:
        lic = fl.license_complete(expr_split[0])
        return formatter.format_license_complete(lic, args.verbose)
    else:
        raise FlameException(f'You can only provide one license to license-full. "{args.license} not allowed"')

def __validations(args):
    validations = []
    if args.validate_spdx:
        validations.append(Validation.SPDX)
    if args.validate_relaxed:
        validations.append(Validation.RELAXED)
    if args.validate_osadl:
        validations.append(Validation.OSADL)

    return validations

def main():

    args = parse()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    formatter = OutputFormatterFactory.formatter(args.output_format)

    config = {}
    config['flame-config'] = args.flame_config
    config['check'] = args.check
    config['additional-license-dir'] = args.additional_license_dir
    config['license-dir'] = args.license_dir
    config['flame-config'] = args.flame_config
    config['license-matrix-file'] = args.license_matrix_file

    try:
        fl = FossLicenses(config=config)
    except Exception as e:
        if args.verbose:
            print(traceback.format_exc())
            print(str(e))

        formatted = formatter.format_error(e, args.verbose)
        print(formatted)
        sys.exit(1)

    if args.func:
        try:
            formatted, warnings = args.func(fl, formatter, args)
            if warnings:
                print(warnings, file=sys.stderr)
            print(formatted)
        except Exception as e:
            if args.verbose:
                print(traceback.format_exc())

            formatted, warnings = formatter.format_error(e, args.verbose)
            print(formatted)
            sys.exit(1)


if __name__ == '__main__':
    main()
