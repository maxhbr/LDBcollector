# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

import re

from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

SPDX_ID = "testlicense"


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    """
    return [atoi(c) for c in re.split(r"(\d+)", text)]


class APILicenseTests(APITestCase):
    """A class to test the naturel workflow with Endpoints.

    This test class is monolitihic, it means that each test is dependent on the success
    of the previous one.

    If the test of the post of a new license fails, then the test will stop because the
    later steps won't be able to be properly tested.
    """

    def step1(self):
        """Test to create a new user"""

        User.objects.create_user("TestUser", "testuser@test.com", "password")
        self.c = APIClient()
        self.assertTrue(self.c.login(username="TestUser", password="password"))

    def step2(self):
        """Test to retrieve licenses"""
        url = "/api/licenses/"
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200)

    def step3(self):
        """Test to post a new license."""
        url = "/api/licenses/"
        data = {
            "spdx_id": SPDX_ID,
            "long_name": "license posted through api",
            "color": "Orange",
            "copyleft": "Strong",
            "foss": "Yes",
            "obligation_set": [],
        }
        r = self.c.post(url, data, format="json")
        self.assertEqual(r.status_code, 201)

    def step4(self):
        """Test to retrieve the created license"""

        # Assumes that the previously created license is the first one in the base
        # (it's the case).
        url = "/api/licenses/1/?format=json"

        r = self.c.get(url)
        self.assertEqual(r.status_code, 200)

    def step5(self):
        """Test to post a Generic obligation"""
        url = "/api/generics/"
        data = {
            "name": "TestGeneric",
            "description": "This generic obligation is for testing purpose.",
            "in_core": "True",
            "metacategory": "IPManagement",
            "passivity": "Active",
        }
        r = self.c.post(url, data, format="json")
        self.assertEqual(r.status_code, 201)

    def step6(self):
        """Test to retrieve the created Generic obligation"""

        # Assumes that the previously created generic obligation is the first one in
        # the base (it's the case).
        url = "/api/generics/1/?format=json"

        r = self.c.get(url)
        self.assertEqual(r.status_code, 200)

    def step7(self):
        """Test to post a new obligation to the previously created license."""
        url = "/api/obligations/"
        data = {
            "license": 1,
            "name": "TestObligation",
            "verbatim": "This obligation is for testing purpose. please delete it.",
            "passivity": "Active",
            "trigger_expl": "DistributionSourceDistributionNonSource",
            "trigger_mdf": "Unmodified",
            "generic_id": 1,
        }
        r = self.c.post(url, data, format="json")
        self.assertEqual(r.status_code, 201)

    def step8(self):
        """Test to retrieve the created obligation"""

        # Assumes that the previously created obligation is the first one in the base
        # (it's the case).
        url = "/api/obligations/1/?format=json"

        r = self.c.get(url)
        self.assertEqual(r.status_code, 200)

    def step9(self):
        """Test to create a new product"""
        url = "/api/products/"

        data = {
            "name": "Test",
            "description": "Please delete me when you see me.",
            "owner": 1,
            "releases": [],
        }

        r = self.c.post(url, data, format="json")
        self.assertEqual(r.status_code, 201)

        url = "/api/products/1/?format=json"

    def step10(self):
        """Test to retrieve the created product"""

        # Assumes that the previously created product is the first one in the base
        # (it's the case).
        url = "/api/products/1/?format=json"

        r = self.c.get(url)
        self.assertEqual(r.status_code, 200)

    def step11(self):
        """Test to create a new release"""
        url = "/api/releases/"

        data = {
            "release_number": "2.0",
            "ship_status": "Active",
            "validation_step": 5,
            "product": 1,
        }

        r = self.c.post(url, data, format="json")
        self.assertEqual(r.status_code, 201)

    def step12(self):
        """Test to retrieve the created release"""

        # Assumes that the previously created product is the first one in the base
        # (it's the case).
        url = "/api/releases/1/?format=json"

        r = self.c.get(url)
        self.assertEqual(r.status_code, 200)

    def step13(self):
        """Test to create a new Component"""
        url = "/api/components/"

        data = {
            "name": "test_component_beta",
            "package_repo": "npm",
            "description": "TestComponent. To be deleted;",
            "programming_language": "javascript",
            "spdx_expression": "",
            "homepage_url": "http://test.com",
            "export_control_status": "",
            "versions": [],
        }

        r = self.c.post(url, data, format="json")
        self.assertEqual(r.status_code, 201)

    def step14(self):
        """Test to retrieve the created Component"""

        # Assumes that the previously created component is the first one in the base
        # (it's the case).
        url = "/api/components/1/?format=json"

        r = self.c.get(url)
        self.assertEqual(r.status_code, 200)

    def step15(self):
        """Test to create a new Version"""
        url = "/api/components/1/versions/"

        data = {
            "version_number": "2.0",
            "declared_license_expr": SPDX_ID + "OR AND",
            "spdx_valid_license_expr": "",
            "corrected_license": SPDX_ID,
        }

        r = self.c.post(url, data, format="json")
        self.assertEqual(r.status_code, 201)

    def step16(self):
        """Test to retrieve the created Version"""

        # Assumes that the previously created component is the first one in the base
        # (it's the case).
        url = "/api/components/1/versions/1/?format=json"

        r = self.c.get(url)
        self.assertEqual(r.status_code, 200)

    def step17(self):
        """Test to create a new Usage"""
        url = "/api/usages/"

        data = {
            "release": 1,
            "version": 1,
            "status": "Validated",
            "addition_method": "Manual",
            "addition_date": "2022-01-19T17:01:40+01:00",
            "linking": "Dynamic",
            "component_modified": "Unmodified",
            "exploitation": "DistributionSourceDistributionNonSource",
            "description": "This is a test Usage",
            "licenses_chosen": [1],
        }

        r = self.c.post(url, data, format="json")
        self.assertEqual(r.status_code, 201)

    def step18(self):
        """Test to retrieve the created Usage"""

        # Assumes that the previously created component is the first one in the base
        # (it's the case).
        url = "/api/usages/1/?format=json"

        r = self.c.get(url)
        self.assertEqual(r.status_code, 200)

    def _steps(self):
        names = dir(self)
        names.sort(
            key=natural_keys
        )  # Allows to have properly sorted steps since there are more than 9
        for name in names:
            if name.startswith("step"):
                yield name, getattr(self, name)

    def test_steps(self):
        for name, step in self._steps():
            step()
