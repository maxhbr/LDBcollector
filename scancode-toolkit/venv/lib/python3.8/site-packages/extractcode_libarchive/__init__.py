#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os.path import abspath
from os.path import dirname
from os.path import join

from plugincode.location_provider import LocationProviderPlugin


class LibarchivePaths(LocationProviderPlugin):
    def get_locations(self):
        curr_dir = dirname(abspath(__file__))
        lib_dir = join(curr_dir, 'lib')
        locations = {
            # extractcode.libarchive.libdir is not used anymore and deprecated
            # but we are keeping it around for now for backward compatibility
            'extractcode.libarchive.libdir': lib_dir,
            'extractcode.libarchive.dll': join(lib_dir, 'libarchive.so'),
        }
        return locations
