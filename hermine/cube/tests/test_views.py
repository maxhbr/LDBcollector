# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

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
