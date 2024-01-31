#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.test import TestCase

from cube.models import LicenseCuration, Version
from cube.utils.ort import hermine_to_ort, export_curations


class ORTToolsTestCase(TestCase):
    fixtures = ["test_data.json"]
    maxDiff = None

    def test_curation_to_ort_dataclass(self):
        LicenseCuration.objects.create(
            version=Version.objects.first(),
            expression_in="LicenseRef-FakeLicense OR AND",
            expression_out="LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
            explanation="Justification for curation 1",
        )
        self.assertEqual(
            hermine_to_ort(LicenseCuration.objects.first()).curations.concluded_license,
            "LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
        )

    def test_export_curations_queryset(self):
        LicenseCuration.objects.create(
            version=Version.objects.first(),
            expression_in="LicenseRef-FakeLicense OR AND",
            expression_out="LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
            explanation="Justification for curation 1",
        )
        LicenseCuration.objects.create(
            version=Version.objects.last(),
            expression_in="LicenseRef-FakeLicense OR AND",
            expression_out="LicenseRef-FakeLicense",
            explanation="Justification for curation 2",
        )
        self.assertEqual(
            export_curations(
                LicenseCuration.objects.all(),
            ),
            """- id: NPM::test_component_alpha:1.0
  curations:
    comment: Justification for curation 1
    concluded_license: LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive
- id: NPM::test_component_alpha:2.0
  curations:
    comment: Justification for curation 2
    concluded_license: LicenseRef-FakeLicense
""",
        )
