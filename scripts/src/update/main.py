import argparse

import OsiDataUpdate
import ScancodeLicensedbDataUpdate
import SpdxDataUpdate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug', default=False)
    parser.add_argument("--spdx", action='store_true', help="Enable SPDX update")
    parser.add_argument("--scancode", action='store_true', help="Enable ScanCode LicenseDB update")
    parser.add_argument("--osi", action='store_true', help="Enable OSI update")

    args = parser.parse_args()

    if args.spdx:
        spdx = SpdxDataUpdate.SpdxDataUpdate(args.debug)
        spdx.process_licenses()
    if args.scancode:
        scancode = ScancodeLicensedbDataUpdate.ScancodeLicensedbDataUpdate(args.debug)
        scancode.process_licenses()
    if args.osi:
        osi = OsiDataUpdate.OsiDataUpdate(args.debug)
        osi.process_licenses()


if __name__ == '__main__':
    main()
