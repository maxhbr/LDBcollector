#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse
import logging 

from flimea.license_db import LicenseDatabase
import flimea.config

DESCRIPTION = """
NAME
  flict (FOSS License Compatibility Tool)

DESCRIPTION
  flict is a Free and Open Source Software tool to verify compatibility between licenses

"""

EPILOG = f"""
CONFIGURATION
  All config files can be found in
  {flimea.config.VAR_DIR}

AUTHOR
  Henrik Sandklef

PROJECT SITE
  https://github.com/vinland-technology/flict

REPORTING BUGS
  File a ticket at https://github.com/vinland-technology/flict/issues

COPYRIGHT
  Copyright (c) 2021 Henrik Sandklef<hesa@sandklef.com>.
  License GPL-3.0-or-later

ATTRIBUTION
  flict is using the license compatibility matrix from osadl.org.


"""

def parse():

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='output verbose information to stderr',
                        default=False)

    parser.add_argument('-c', '--check',
                        action='store_true',
                        help='check all license files against JSON schema when initializing',
                        default=False)

    subparsers = parser.add_subparsers(help='Sub commands')
    
    # alias
    parser_a = subparsers.add_parser(
        'alias', help='show license matching alias')
    parser_a.set_defaults(which="alias", func=alias)
    parser_a.add_argument('license_expression', type=str, 
                          help='license expression to display compatibility for')
    parser_a.add_argument('--spdx', action='store_true',
                          help='')
    parser_a.add_argument('--scancode-key', '-sk', action='store_true',
                          help='')
    parser_a.add_argument('--identified-via', '-iv', action='store_true',
                          help='')

    

    args = parser.parse_args()

    return args

def alias(ldb, args):
    ret = []
    if args.spdx:
        ret.append(f'spdxid: {ldb.license(args.license_expression)["license"]["spdxid"]}')
    if args.scancode_key:
        ret.append(f'scancode_key: {ldb.license(args.license_expression)["license"]["scancode_key"]}')
    if args.identified_via:
        ret.append(f'identified via: "{ldb.license(args.license_expression)["identified_license"]["identified_via"]}"')
    else:
        ret.append(ldb.license(args.license_expression))
    print(f'{", ".join(ret)}')
    
    

def main():
    
    args = parse()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    ldb = LicenseDatabase(check=args.check)

    if args.func:
        args.func(ldb, args)
        


if __name__ == '__main__':
    main()

