#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.models import User
from rest_framework.test import APITestCase as BaseAPITestCase


class ForceLoginMixin:
    def setUp(self):
        self.user = User.objects.get(username="admin")
        self.client.force_login(self.user)


class BaseHermineAPITestCase(BaseAPITestCase):
    SPDX_ID = "LicenseRef-fakeLicense-1.0"

    def setUp(self):
        self.user = User.objects.create_superuser(
            "TestUser", "testuser@test.com", "password"
        )
        self.client.force_login(self.user)

    def create_license(self):
        url = "/api/licenses/"
        data = {
            "spdx_id": self.SPDX_ID,
            "long_name": "license posted through api",
            "allowed": "context",
            "copyleft": "Strong",
            "foss": "Yes",
            "obligation_set": [],
        }
        return self.client.post(url, data)

    def create_component(self):
        url = "/api/components/"
        data = {
            "name": "test_component_beta",
            "purl_type": "npm",
            "description": "TestComponent. To be deleted;",
            "programming_language": "javascript",
            "spdx_expression": "",
            "homepage_url": "http://test.com",
            "export_control_status": "",
            "versions": [],
        }
        return self.client.post(url, data)

    def create_component_other(self):
        url = "/api/components/"
        data = {
            "name": "test_component_beta_other",
            "purl_type": "composer",
            "description": "Other TestComponent. To be deleted too;",
            "programming_language": "PHP",
            "spdx_expression": "",
            "homepage_url": "http://test.com",
            "export_control_status": "",
            "versions": [],
        }
        return self.client.post(url, data)

    def create_release(self):
        url = "/api/releases/"
        data = {
            "release_number": "2.0",
            "ship_status": "Active",
            "validation_step": 5,
            "product": 1,
            "commit": "a9eb85ea214a6cfa6882f4be041d5cce7bee3e45",
        }
        return self.client.post(url, data)

    def create_product(self):
        url = "/api/products/"
        data = {
            "name": "Test",
            "description": "Please delete me when you see me.",
            "owner": 1,
            "releases": [],
        }
        return self.client.post(url, data)

    def create_version(self):
        url = "/api/components/1/versions/"
        data = {
            "version_number": "2.0",
            "declared_license_expr": self.SPDX_ID + "OR AND",
            "spdx_valid_license_expr": "",
            "corrected_license": self.SPDX_ID,
        }
        return self.client.post(url, data)
