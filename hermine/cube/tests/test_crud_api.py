# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.urls import reverse

from cube.models import (
    Usage,
    Release,
)
from .mixins import BaseHermineAPITestCase


class APICRUDTests(BaseHermineAPITestCase):
    """A class to test the naturel workflow with Endpoints.

    This test class is monolitihic, it means that each test is dependent on the success
    of the previous one.

    If the test of the post of a new license fails, then the test will stop because the
    later steps won't be able to be properly tested.
    """

    def test_retrieve_license(self):
        """Test to retrieve licenses"""
        url = "/api/licenses/"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_post_retrieve_license(self):
        """Test to post a new license."""
        r = self.create_license()
        self.assertEqual(r.status_code, 201)

        url = "/api/licenses/1/?format=json"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_post_retrieve_generic(self):
        """Test to post a Generic obligation"""
        url = "/api/generics/"
        data = {
            "name": "TestGeneric",
            "description": "This generic obligation is for testing purpose.",
            "in_core": "True",
            "metacategory": "IPManagement",
            "passivity": "Active",
        }
        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 201)

        url = "/api/generics/1/?format=json"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_post_retrieve_obligations(self):
        """Test to post a new obligation to the previously created license."""
        url = "/api/licenses/"
        data = {
            "spdx_id": self.SPDX_ID,
            "long_name": "license posted through api",
            "color": "Orange",
            "copyleft": "Strong",
            "foss": "Yes",
            "obligation_set": [],
        }
        self.client.post(url, data)

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
        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 201)

        url = "/api/obligations/1/?format=json"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_post_retrieve_product(self):
        """Test to create a new product"""
        r = self.create_product()
        self.assertEqual(r.status_code, 201)

        url = "/api/products/1/?format=json"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_post_retrieve_release(self):
        """Test to create a new release"""
        self.create_product()

        r = self.create_release()
        self.assertEqual(r.status_code, 201)

        url = "/api/releases/1/?format=json"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_post_retrieve_component(self):
        """Test to create a new Component"""
        r = self.create_component()
        self.assertEqual(r.status_code, 201)

        url = "/api/components/1/?format=json"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_post_retrieve_component_filter(self):
        """Test to filter Components list on name and package_repo"""
        r = self.create_component()
        self.assertEqual(r.status_code, 201)

        r = self.create_component_other()
        self.assertEqual(r.status_code, 201)

        url = "/api/components/"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 2)

        url = "/api/components/?name=test_component_beta_other&package_repo=composer"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

        url = "/api/components/?name=test_component_beta_other"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

        url = "/api/components/?package_repo=composer"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

        url = "/api/components/?name=test_component_beta_other&package_repo=npm"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 0)

    def test_post_retrieve_version(self):
        self.create_component()

        r = self.create_version()
        self.assertEqual(r.status_code, 201)

        url = "/api/components/1/versions/1/?format=json"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_post_retrieve_usage(self):
        """Test to create a new Usage"""
        self.create_product()
        self.create_release()
        self.create_component()
        self.create_version()
        self.create_license()

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

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 201)

        url = "/api/usages/1/?format=json"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_post_retrieve_license_choice(self):
        """Test to create a new Usage"""
        self.create_product()
        self.create_release()
        self.create_component()
        self.create_version()

        url = "/api/choices/"
        data = {
            "product": 1,
            "component": 1,
            "expression_in": "testlicense1 OR testlicense2",
            "expression_out": "LicenseRef-testlicense1",
        }

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 201)

        url = "/api/choices/1/?format=json"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["author"], self.user.pk)

    def test_post_retreive_exploitation(self):
        self.create_product()
        self.create_release()

        release_id = Release.objects.first().pk

        url = reverse("cube:releases-exploitations-list", args=[release_id])
        data = {
            "scope": "testscope",
            "project": "testproject",
            "exploitation": Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
        }
        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 201)

        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
