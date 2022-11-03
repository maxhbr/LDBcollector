# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from urllib.parse import quote

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cube.forms import CreateLicenseCurationForm
from cube.models import LicenseCuration, LicenseChoice, Exploitation
from .mixins import ForceLoginMixin


class UnauthenticatedTestCase(TestCase):
    fixtures = ["test_data.json"]
    urls = [
        reverse("cube:root"),
        reverse("cube:about"),
        reverse("cube:products"),
        reverse("cube:product_detail", kwargs={"pk": 1}),
        reverse("cube:components"),
        reverse("cube:component_detail", kwargs={"pk": 2}),
        reverse("cube:release_validation", kwargs={"pk": 1}),
        reverse("cube:release_summary", kwargs={"pk": 1}),
        reverse("cube:release_bom", kwargs={"release_pk": 1}),
        reverse("cube:release_bom_export", kwargs={"pk": 1}),
        reverse("cube:licenses"),
        reverse("cube:license", kwargs={"pk": 3}),
        reverse("cube:generics"),
        reverse("cube:generic", kwargs={"pk": 1}),
    ]

    def test_protected_views(self):
        for url in self.urls:
            res = self.client.get(url)
            self.assertRedirects(
                res, reverse("login") + "?next=" + quote(url, safe="/")
            )
        self.client.force_login(User.objects.get(username="admin"))
        for url in self.urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200)


class ProductViewsTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_products_view(self):
        url = reverse("cube:products")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "test_product")

    def test_product_detail_view(self):
        url = reverse("cube:product_detail", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "This is for testing purpose")  # product description


class ComponentViewsTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_components_view(self):
        url = reverse("cube:components")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "3rd Party Components")
        self.assertContains(res, "test_component_alpha")  # component name

    def test_component_detail_view(self):
        url = reverse("cube:component_detail", kwargs={"pk": 2})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "test_component_alpha")  # component name
        self.assertContains(res, "test_product")  # product in which component is used


class LicenseViewsTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_license_details_display_obligations(self):
        res = self.client.get(reverse("cube:license", args=[3]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Test License Distribution Unmodified")


class ReleaseViewsTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_release_summary_with_multiple_exploitation_choice(self):
        url = reverse("cube:release_summary", kwargs={"pk": 1})
        Exploitation.objects.create(release_id=1, scope="back")
        Exploitation.objects.create(release_id=1, scope="front")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Exploitation decisions")

    def test_release_validation_view(self):
        url = reverse("cube:release_validation", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Release: 1.0")  # release number

    def test_release_bom_view(self):
        url = reverse("cube:release_bom", kwargs={"release_pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(
            res, "test_component_alpha"
        )  # test component alpha is used in release 1

    def test_create_license_curation(self):
        url = reverse("cube:licensecuration_create", args=[1])
        res = self.client.post(
            url,
            {
                "expression_out": "MIT",
                "component_version": CreateLicenseCurationForm.ANY,
            },
        )
        self.assertRedirects(res, reverse("cube:release_validation", args=[1]))
        self.assertEqual(LicenseCuration.objects.all().count(), 1)
        self.assertEqual(LicenseChoice.objects.all().count(), 0)


class ExportSBOMTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_export_simple_sbom(self):
        url = reverse("cube:release_bom_export", args=[1])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "name,version")
        self.assertContains(res, "LicenseRef-FakeLicense OR AND")
