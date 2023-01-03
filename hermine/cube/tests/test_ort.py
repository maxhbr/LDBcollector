#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.test import TestCase

from cube.models import LicenseCuration, Version
from cube.utils.ort import hermine_to_ort, CurationEntry


class ORTToolsTestCase(TestCase):
    fixtures = ["test_data.json"]

    def test_export_curation(self):
        LicenseCuration.objects.create(
            version=Version.objects.first(),
            expression_in="LicenseRef-FakeLicense OR AND",
            expression_out="LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
        )
        self.assertEqual(
            hermine_to_ort(LicenseCuration.objects.first()).curations.concluded_license,
            "LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
        )
