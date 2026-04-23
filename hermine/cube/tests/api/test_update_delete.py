# SPDX-FileCopyrightText: 2026 Maud Royer <hello@maudroyer.fr>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.urls import reverse

from cube.models import License, LicensePolicy, Product, Release, Exploitation
from .mixins import BaseHermineAPITestCase


class ProductAPIUpdateDeleteTests(BaseHermineAPITestCase):
    def setUp(self):
        super().setUp()
        r = self.create_product()
        self.assertEqual(r.status_code, 201)
        self.product_id = r.data["id"]
        self.detail_url = reverse("cube:api:products-detail", args=[self.product_id])

    def test_update_product(self):
        r = self.client.put(
            self.detail_url,
            {
                "name": "Updated Product",
                "description": "Updated description",
                "owner": 1,
                "releases": [],
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            Product.objects.get(pk=self.product_id).name, "Updated Product"
        )

    def test_patch_product(self):
        r = self.client.patch(self.detail_url, {"name": "Patched Product"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            Product.objects.get(pk=self.product_id).name, "Patched Product"
        )

    def test_delete_product(self):
        r = self.client.delete(self.detail_url)
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Product.objects.filter(pk=self.product_id).exists())

    def test_filter_product_by_name(self):
        r = self.client.post(
            reverse("cube:api:products-list"),
            {
                "name": "Other Product",
                "description": "Other",
                "owner": 1,
                "releases": [],
            },
        )
        self.assertEqual(r.status_code, 201)
        r = self.client.get(reverse("cube:api:products-list") + "?name=Test")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)


class LicenseAPIUpdateDeleteTests(BaseHermineAPITestCase):
    def setUp(self):
        super().setUp()
        r = self.create_license()
        self.assertEqual(r.status_code, 201)
        self.detail_url = reverse("cube:api:licenses-detail", args=[self.SPDX_ID])

    def test_update_license(self):
        r = self.client.put(
            self.detail_url,
            {
                "spdx_id": self.SPDX_ID,
                "long_name": "Updated license name",
                "copyleft": "Strong",
                "foss": "Yes",
                "obligation_set": [],
            },
        )
        self.assertEqual(r.status_code, 200)
        lic = License.objects.get(spdx_id=self.SPDX_ID)
        self.assertEqual(lic.long_name, "Updated license name")

    def test_patch_license(self):
        r = self.client.patch(
            self.detail_url,
            {"copyleft": "Weak", "obligation_set": []},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        lic = License.objects.get(spdx_id=self.SPDX_ID)
        self.assertEqual(lic.copyleft, "Weak")

    def test_delete_license(self):
        r = self.client.delete(self.detail_url)
        self.assertEqual(r.status_code, 204)
        self.assertFalse(License.objects.filter(spdx_id=self.SPDX_ID).exists())

    def test_lookup_by_numeric_id(self):
        lic = License.objects.get(spdx_id=self.SPDX_ID)
        url = reverse("cube:api:licenses-detail", args=[lic.pk])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["spdx_id"], self.SPDX_ID)


class LicensePolicyAPITests(BaseHermineAPITestCase):
    def setUp(self):
        super().setUp()
        r = self.create_license()
        self.assertEqual(r.status_code, 201)
        self.policy_url = reverse("cube:api:licenses-policy", args=[self.SPDX_ID])

    def test_get_policy(self):
        r = self.client.get(self.policy_url)
        self.assertEqual(r.status_code, 200)

    def test_update_policy(self):
        r = self.client.patch(
            self.policy_url,
            {
                "allowed": "always",
            },
        )
        self.assertEqual(r.status_code, 200)
        policy = LicensePolicy.objects.get(license__spdx_id=self.SPDX_ID)
        self.assertEqual(policy.allowed, "always")


class ReleaseAPIUpdateDeleteTests(BaseHermineAPITestCase):
    def setUp(self):
        super().setUp()
        r = self.create_product()
        self.assertEqual(r.status_code, 201)
        r = self.create_release()
        self.assertEqual(r.status_code, 201)
        self.release_id = r.data["id"]
        self.detail_url = reverse("cube:api:releases-detail", args=[self.release_id])

    def test_patch_release(self):
        r = self.client.patch(self.detail_url, {"release_number": "3.0"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Release.objects.get(pk=self.release_id).release_number, "3.0")

    def test_delete_release(self):
        r = self.client.delete(self.detail_url)
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Release.objects.filter(pk=self.release_id).exists())


class ExploitationAPIUpdateDeleteTests(BaseHermineAPITestCase):
    def setUp(self):
        super().setUp()
        r = self.create_product()
        self.assertEqual(r.status_code, 201)
        r = self.create_release()
        self.assertEqual(r.status_code, 201)
        self.release_id = r.data["id"]
        url = reverse("cube:api:releases-exploitations-list", args=[self.release_id])
        r = self.client.post(
            url,
            {
                "scope": "testscope",
                "project": "testproject",
                "exploitation": "DistributionSourceDistributionNonSource",
            },
        )
        self.assertEqual(r.status_code, 201)
        self.exploitation_id = r.data["id"]

    def test_patch_exploitation(self):
        url = reverse(
            "cube:api:releases-exploitations-detail",
            args=[self.release_id, self.exploitation_id],
        )
        r = self.client.patch(url, {"scope": "updated_scope"})
        self.assertEqual(r.status_code, 200)

    def test_delete_exploitation(self):
        url = reverse(
            "cube:api:releases-exploitations-detail",
            args=[self.release_id, self.exploitation_id],
        )
        r = self.client.delete(url)
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Exploitation.objects.filter(pk=self.exploitation_id).exists())
