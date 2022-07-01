# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from urllib.parse import quote

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode


class ForceLoginMixin:
    def setUp(self):
        self.client.force_login(User.objects.get(username="admin"))


class UnauthenticatedTestCase(TestCase):
    fixtures = ["test_data.json"]
    urls = [
        reverse("cube:root"),
        reverse("cube:about"),
        reverse("cube:products"),
        reverse("cube:product_detail", kwargs={"pk": 1}),
        reverse("cube:components"),
        reverse("cube:component_detail", kwargs={"pk": 2}),
        reverse("cube:release_detail", kwargs={"pk": 1}),
        reverse("cube:release_bom", kwargs={"pk": 1}),
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
        self.assertContains(res, "Top 10 Most used")
        self.assertContains(res, "test_component_alpha")  # component name

    def test_component_detail_view(self):
        url = reverse("cube:component_detail", kwargs={"pk": 2})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "test_component_alpha")  # component name
        self.assertContains(res, "test_product")  # product in which component is used


class ReleaseViewsTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_release_detail_view(self):
        url = reverse("cube:release_detail", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Release: 1.0")  # release number

    def test_release_bom_view(self):
        url = reverse("cube:release_bom", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(
            res, "test_component_alpha"
        )  # test component alpha is used in release 1
