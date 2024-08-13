#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.contrib.auth.models import User
from django.urls import reverse, URLPattern
from rest_framework.test import APITestCase


def get_api_patterns():
    from cube.urls_api import urlpatterns

    return [
        pattern.name
        for pattern in urlpatterns
        if isinstance(pattern, URLPattern)
        and hasattr(pattern, "name")
        and pattern.name is not None
        and ("-list" in pattern.name)
    ]


class PermissionsTestCase(APITestCase):
    def test_anonymous_unauthenticated(self):
        for pattern in get_api_patterns():
            with self.subTest(pattern=pattern):
                response = self.client.get(reverse(f"cube:api:{pattern}"))
                if response.status_code == 405:
                    response = self.client.post(reverse(f"cube:api:{pattern}"))
                self.assertEqual(response.status_code, 401)

    def test_no_permissions_user(self):
        User.objects.create_user("test", "testuser@test.com", "password")
        self.client.login(username="test", password="password")
        for pattern in get_api_patterns():
            with self.subTest(pattern=pattern):
                response = self.client.get(reverse(f"cube:api:{pattern}"))
                if response.status_code == 405:
                    response = self.client.post(reverse(f"cube:api:{pattern}"))
                self.assertNotEqual(response.status_code, 403)
                self.client.logout()

    def test_admin(self):
        User.objects.create_superuser("admin", "adminuser@test.com", "password")
        self.client.login(username="admin", password="password")
        for pattern in get_api_patterns():
            with self.subTest(pattern=pattern):
                response = self.client.get(reverse(f"cube:api:{pattern}"))
                if response.status_code == 405:
                    response = self.client.post(reverse(f"cube:api:{pattern}"))
                self.assertNotEqual(response.status_code, 403)
                self.client.logout()
