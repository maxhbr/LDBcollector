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


class MsitoolsPaths(LocationProviderPlugin):
    def get_locations(self):
        curr_dir = dirname(abspath(__file__))
        bin_dir = join(curr_dir, 'bin')
        locations = {
            'packagedcode_msitools.msiinfo': join(bin_dir, 'msiinfo'),
        }
        return locations
