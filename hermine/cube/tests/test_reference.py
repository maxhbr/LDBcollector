#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only


from django.test import TestCase

from cube.models import License, Generic
from cube.utils.reference import get_license_ref_dict


class ReferenceTestCase(TestCase):
    databases = {"default", "shared"}
    fixtures = ["test_data.json"]

    def setUp(self):
        get_license_ref_dict.cache_clear()

    def test_license_reference_diff_equal(self):
        lic = License.objects.get(spdx_id="LicenseRef-FakeLicense-1.0")
        self.assertEqual(lic.reference_diff, 0)

    def test_license_reference_diff_different(self):
        lic = License.objects.get(spdx_id="LicenseRef-FakeLicense-1.0")
        lic.copyleft = License.COPYLEFT_WEAK
        lic.save()

        self.assertEqual(lic.reference_diff, 1)

    def test_license_reference_diff_absent(self):
        License.objects.using("shared").get(
            spdx_id="LicenseRef-FakeLicense-1.0"
        ).delete()
        lic = License.objects.get(spdx_id="LicenseRef-FakeLicense-1.0")

        self.assertEqual(lic.reference_diff, -1)

    def test_diff_is_cached(self):
        lic = License.objects.get(spdx_id="LicenseRef-FakeLicense-1.0")
        self.assertEqual(lic.reference_diff, 0)
        shared_lic = License.objects.using("shared").get(
            spdx_id="LicenseRef-FakeLicense-1.0"
        )
        shared_lic.name = "Fake License modified"
        shared_lic.save()

        lic = License.objects.get(spdx_id="LicenseRef-FakeLicense-1.0")
        self.assertEqual(lic.reference_diff, 0)

    def test_diff_includes_obligations(self):
        lic = License.objects.get(spdx_id="LicenseRef-FakeLicense-1.0")
        obligation = lic.obligation_set.first()
        obligation.generic = Generic.objects.first()
        obligation.save()

        self.assertEqual(lic.reference_diff, 1)
