# SPDX-FileCopyrightText: 2026 Maud Royer <hello@maudroyer.fr>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.urls import reverse

from cube.models import License, LicensePolicy, Product, Release, Exploitation
from .mixins import BaseHermineAPITestCase


class ProductAPIUpdateDeleteTests(BaseHermineAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_product()

    def test_update_product(self):
        r = self.client.put(
            "/api/products/1/",
            {
                "name": "Updated Product",
                "description": "Updated description",
                "owner": 1,
                "releases": [],
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Product.objects.get(pk=1).name, "Updated Product")

    def test_patch_product(self):
        r = self.client.patch("/api/products/1/", {"name": "Patched Product"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Product.objects.get(pk=1).name, "Patched Product")

    def test_delete_product(self):
        r = self.client.delete("/api/products/1/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Product.objects.filter(pk=1).exists())

    def test_filter_product_by_name(self):
        self.client.post(
            "/api/products/",
            {
                "name": "Other Product",
                "description": "Other",
                "owner": 1,
                "releases": [],
            },
        )
        r = self.client.get("/api/products/?name=Test")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)


class LicenseAPIUpdateDeleteTests(BaseHermineAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_license()

    def test_update_license(self):
        r = self.client.put(
            f"/api/licenses/{self.SPDX_ID}/",
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
            f"/api/licenses/{self.SPDX_ID}/",
            {"copyleft": "Weak", "obligation_set": []},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        lic = License.objects.get(spdx_id=self.SPDX_ID)
        self.assertEqual(lic.copyleft, "Weak")

    def test_delete_license(self):
        r = self.client.delete(f"/api/licenses/{self.SPDX_ID}/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(License.objects.filter(spdx_id=self.SPDX_ID).exists())

    def test_lookup_by_numeric_id(self):
        lic = License.objects.get(spdx_id=self.SPDX_ID)
        r = self.client.get(f"/api/licenses/{lic.pk}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["spdx_id"], self.SPDX_ID)


class LicensePolicyAPITests(BaseHermineAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_license()

    def test_get_policy(self):
        r = self.client.get(f"/api/licenses/{self.SPDX_ID}/policy/")
        self.assertEqual(r.status_code, 200)

    def test_update_policy(self):
        r = self.client.patch(
            f"/api/licenses/{self.SPDX_ID}/policy/",
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
        self.create_product()
        self.create_release()

    def test_patch_release(self):
        r = self.client.patch("/api/releases/1/", {"release_number": "3.0"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Release.objects.get(pk=1).release_number, "3.0")

    def test_delete_release(self):
        r = self.client.delete("/api/releases/1/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Release.objects.filter(pk=1).exists())


class ExploitationAPIUpdateDeleteTests(BaseHermineAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_product()
        self.create_release()
        release_id = Release.objects.first().pk
        url = reverse("cube:api:releases-exploitations-list", args=[release_id])
        self.client.post(
            url,
            {
                "scope": "testscope",
                "project": "testproject",
                "exploitation": "DistributionSourceDistributionNonSource",
            },
        )
        self.release_id = release_id
        self.exploitation_id = Exploitation.objects.first().pk

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
