#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import argparse

from src.update.OsiDataUpdate import OsiDataUpdate
from src.update.ScancodeLicensedbDataUpdate import ScancodeLicensedbDataUpdate
from src.update.SpdxDataUpdate import SpdxDataUpdate
import src.validate.data_validation as validation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug', default=False)
    parser.add_argument("--spdx", action='store_true', help="Enable SPDX update")
    parser.add_argument("--scancode", action='store_true', help="Enable ScanCode LicenseDB update")
    parser.add_argument("--osi", action='store_true', help="Enable OSI update")

    args = parser.parse_args()

    if args.spdx:
        spdx = SpdxDataUpdate(args.debug)
        spdx.process_licenses()
    if args.scancode:
        scancode = ScancodeLicensedbDataUpdate(args.debug)
        scancode.process_licenses()
    if args.osi:
        osi = OsiDataUpdate(args.debug)
        osi.process_licenses()

    validation.main()


if __name__ == '__main__':
    main()
