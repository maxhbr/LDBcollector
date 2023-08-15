#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse
import logging 

from flame.license_db import LicenseDatabase
import flame.config
from flame.format import OUTPUT_FORMATS
from flame.format import OutputFormatterFactory

def parse():

    parser = argparse.ArgumentParser(
        description=flame.config.DESCRIPTION,
        epilog=flame.config.EPILOG,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='output verbose information',
                        default=False)

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='output debug information to stderr',
                        default=False)

    parser.add_argument('-c', '--check',
                        action='store_true',
                        help='check all license files against JSON schema when initializing',
                        default=False)

    parser.add_argument('-of', '--output-format',
                        type=str,
                        help=f'Chose output format. Available formats: {", ".join(OUTPUT_FORMATS)}',
                        default="text")

    subparsers = parser.add_subparsers(help='Sub commands')
    
    # aliases
    parser_a = subparsers.add_parser(
        'aliases', help='show all aliases')
    parser_a.set_defaults(which='aliases', func=aliases)
    
    # identify
    parser_i = subparsers.add_parser(
        'identify', help='show license matching supplied license')
    parser_i.set_defaults(which='identify', func=identify)
    parser_i.add_argument('license', type=str, help='license name to identify')
    parser_i.add_argument('--spdx', '-s', action='store_true',
                          help='')
    parser_i.add_argument('--scancode-key', '-sk', action='store_true',
                          help='')
    parser_i.add_argument('--identified-via', '-iv', action='store_true',
                          help='')

    # compatibility
    parser_c = subparsers.add_parser(
        'compat', help='display license with same compatibility as supplied license')
    parser_c.set_defaults(which='compat', func=compatibility)
    parser_c.add_argument('license', type=str, help='license name to display')

    args = parser.parse_args()

    return args

def aliases(ldb, formatter, args):
    all_aliases = ldb.aliases_list()
    return formatter.format_identified_list(all_aliases, args.verbose)

def compatibility(ldb, formatter, args):
    compat = ldb.compatibility_as(args.license)
    return formatter.format_compat(compat, args.verbose)
    
def identify(ldb, formatter, args):
    identified_license = ldb.license(args.license)
    return formatter.format_identified(identified_license, args.verbose)
    
    

def main():
    
    args = parse()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    ldb = LicenseDatabase(check=args.check)
    
    formatter = OutputFormatterFactory.formatter(args.output_format)
    
    if args.func:
        formatted = args.func(ldb, formatter, args)
        print(formatted)

        

if __name__ == '__main__':
    main()

