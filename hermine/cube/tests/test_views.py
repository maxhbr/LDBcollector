# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from urllib.parse import quote

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class MiscViewsTestCase(TestCase):
    def test_home(self):
        url = reverse("cube:root")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_about(self):
        url = reverse("cube:about")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)


class UnauthenticatedTestCase(TestCase):
    urls = [reverse("cube:products"), reverse("cube:product_detail", kwargs={"pk": 1})]

    def test_protected_views(self):
        for url in self.urls:
            res = self.client.get(url)
            self.assertRedirects(
                res, reverse("login") + "?next=" + quote(url, safe="/")
            )


class ProductViewsTestCase(TestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        self.client.force_login(User.objects.get(username="admin"))

    def test_products_view(self):
        url = reverse("cube:products")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "test_product")

    def test_product_detail_view(self):
        url = reverse("cube:product_detail", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "This is for testing purpose")
