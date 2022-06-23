# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase as BaseAPITestCase

from cube.models import LINKING_PACKAGE, Version, LicenseChoice, Derogation
from cube.utils.licenses import handle_licenses_json

SPDX_ID = "testlicense"


class APITestCase(BaseAPITestCase):
    def setUp(self):
        User.objects.create_user("TestUser", "testuser@test.com", "password")
        self.client.login(username="TestUser", password="password")

    def create_license(self):
        url = "/api/licenses/"
        data = {
            "spdx_id": SPDX_ID,
            "long_name": "license posted through api",
            "color": "Orange",
            "copyleft": "Strong",
            "foss": "Yes",
            "obligation_set": [],
        }
        return self.client.post(url, data)

    def create_component(self):
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
            "declared_license_expr": SPDX_ID + "OR AND",
            "spdx_valid_license_expr": "",
            "corrected_license": SPDX_ID,
        }
        return self.client.post(url, data)


class APICRUDTests(APITestCase):
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
            "spdx_id": SPDX_ID,
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


class ReleaseStepsAPITestCase(APITestCase):
    def import_licenses(cls):
        with open("cube/fixtures/fake_licenses.json") as licenses_file:
            handle_licenses_json(licenses_file.read())

    def test_simple_sbom(self):
        self.create_product()
        self.create_release()

        with open("cube/fixtures/fake_sbom.json", "r") as sbom_file:
            url = reverse("cube:upload_spdx-list")
            res = self.client.post(
                url,
                {
                    "spdx_file": sbom_file,
                    "release": 1,
                    "replace": False,
                    "linking": LINKING_PACKAGE,
                },
                format="multipart",
            )
        self.assertEqual(res.status_code, 201)

        # Step 1
        res = self.client.get(reverse("cube:release-validation-1", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)
        self.assertEqual(len(res.data["unnormalized_usages"]), 1)

        ## Simulate fixing manually
        Version.objects.filter(component__name="dependency2").update(
            spdx_valid_license_expr="LicenseRef-fakeLicense-Permissive-1.0"
        )
        res = self.client.get(reverse("cube:release-validation-1", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)

        # Step 2
        res = self.client.post(
            reverse("cube:release-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["validation_step"], 2)  # unknown license
        res = self.client.get(reverse("cube:release-validation-2", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)
        self.assertEqual(len(res.data["licenses_to_create"]), 2)

        self.import_licenses()
        res = self.client.get(reverse("cube:release-validation-2", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)

        # Step 3
        res = self.client.post(
            reverse("cube:release-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], 3)  # ANDs confirmation
        res = self.client.get(reverse("cube:release-validation-3", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)

        ## Simulate fixing manually
        Version.objects.filter(component__name="dependency3").update(
            corrected_license="LicenseRef-fakeLicense-WeakCopyleft-1.0 OR LicenseRef-fakeLicense-Permissive-1.0"
        )
        res = self.client.get(reverse("cube:release-validation-3", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)

        # Step 4
        res = self.client.post(
            reverse("cube:release-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], 4)  # License choices
        res = self.client.get(reverse("cube:release-validation-4", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)
        self.assertEqual(len(res.data["to_resolve"]), 1)

        ## Simulate
        LicenseChoice.objects.create(
            expression_in="LicenseRef-fakeLicense-WeakCopyleft-1.0 OR LicenseRef-fakeLicense-Permissive-1.0",
            expression_out="LicenseRef-fakeLicense-WeakCopyleft-1.0",
        )
        res = self.client.get(reverse("cube:release-validation-4", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)

        # Step 5
        res = self.client.post(
            reverse("cube:release-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], 5)  # policy compatibility
        res = self.client.get(reverse("cube:release-validation-5", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)

        ## Simulate fixing
        Derogation.objects.create(license_id=2, release_id=1)
        res = self.client.get(reverse("cube:release-validation-5", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)

        ## Finished
        res = self.client.post(
            reverse("cube:release-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], 6)
