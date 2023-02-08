#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.urls import reverse

from cube.models import (
    Usage,
    LicenseCuration,
    Component,
    Exploitation,
    Derogation,
    License,
)
from cube.utils.licenses import handle_licenses_json
from cube.utils.release_validation import (
    STEP_CURATION,
    STEP_CONFIRM_AND,
    STEP_EXPLOITATIONS,
    STEP_CHOICES,
    STEP_POLICY,
)
from .mixins import BaseHermineAPITestCase


class ReleaseStepsAPITestCase(BaseHermineAPITestCase):
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
                    "linking": Usage.LINKING_DYNAMIC,
                },
                format="multipart",
            )
        self.assertEqual(res.status_code, 201)

        res = self.client.post(
            reverse("cube:releases-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], 0)

        # Step 1
        res = self.client.get(reverse("cube:releases-validation-1", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)
        self.assertEqual(len(res.data["invalid_expressions"]), 2)
        self.assertEqual(
            Usage.objects.filter(
                license_expression="LicenseRef-fakeLicense-ContextAllowed-1.0"
            ).count(),
            2,  # valid and wrong-concluded
        )

        ## Simulate fixing manually
        ### Licenses with no concluded license
        LicenseCuration.objects.create(
            expression_in="Allowed-1.0 AND ContextAllowed-1.0",
            expression_out="LicenseRef-fakeLicense-Allowed-1.0 OR LicenseRef-fakeLicense-ContextAllowed-1.0",
        )
        LicenseCuration.objects.create(
            component=Component.objects.get(name="no-assertion-dependency"),
            expression_in="NOASSERTION",
            expression_out="LicenseRef-fakeLicense-Allowed-1.0",
        )
        ### Licenses with wrong concluded licenses
        LicenseCuration.objects.create(
            component=Component.objects.get(name="wrong-concluded-dependency"),
            expression_in="LicenseRef-fakeLicense-ContextAllowed-1.0",
            expression_out="LicenseRef-fakeLicense-Allowed-1.0 AND LicenseRef-fakeLicense-NotAnalyzed-1.0",
        )
        # Is everything right ?
        res = self.client.get(reverse("cube:releases-validation-1", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)
        self.assertTrue(
            License.objects.filter(
                spdx_id="LicenseRef-fakeLicense-NotAnalyzed-1.0"
            ).exists()
        )

        res = self.client.post(
            reverse("cube:releases-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], STEP_CURATION)

        # Step 2
        self.import_licenses()
        res = self.client.get(reverse("cube:releases-validation-2", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)

        ## Simulate fixing manually
        LicenseCuration.objects.create(
            expression_in="LicenseRef-fakeLicense-Allowed-1.0 AND LicenseRef-fakeLicense-ContextAllowed-1.0",
            expression_out="LicenseRef-fakeLicense-Allowed-1.0 OR LicenseRef-fakeLicense-ContextAllowed-1.0",
        )
        res = self.client.get(reverse("cube:releases-validation-2", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)
        res = self.client.post(
            reverse("cube:releases-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], STEP_CONFIRM_AND)

        # Step 3
        res = self.client.get(reverse("cube:releases-validation-3", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)
        self.assertEqual(len(res.data["unset_scopes"]), 1)

        ## Create exploitation manually
        Exploitation.objects.create(
            release_id=1,
            scope=Usage.DEFAULT_SCOPE,
            project=Usage.DEFAULT_PROJECT,
            exploitation=Usage.EXPLOITATION_INTERNAL,
        )
        res = self.client.get(reverse("cube:releases-validation-3", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)

        res = self.client.post(
            reverse("cube:releases-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], STEP_EXPLOITATIONS)

        # Step 4
        res = self.client.get(reverse("cube:releases-validation-4", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)
        self.assertEqual(len(res.data["to_resolve"]), 2)

        ## Create choice through API
        res = self.client.post(
            reverse("cube:choices-list"),
            data={
                "expression_in": "LicenseRef-fakeLicense-Allowed-1.0 OR LicenseRef-fakeLicense-ContextAllowed-1.0",
                "expression_out": "LicenseRef-fakeLicense-Allowed-1.0",
            },
        )
        res = self.client.get(reverse("cube:releases-validation-4", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)
        self.assertEqual(
            len(res.data["resolved"]), 2
        )  # ambiguous-dependency and invalid-dependency

        res = self.client.post(
            reverse("cube:releases-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], STEP_CHOICES)

        # Step 5
        res = self.client.post(
            reverse("cube:releases-update-validation", kwargs={"id": 1})
        )
        res = self.client.get(reverse("cube:releases-validation-5", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)
        self.assertEqual(
            len(res.data["usages_lic_unknown"]), 1
        )  # wrong-concluded-dependency
        self.assertEqual(
            len(res.data["usages_lic_context_allowed"]), 1
        )  # spdx-valid-dependency

        ## Simulate fixing
        Derogation.objects.create(
            license=License.objects.get(
                spdx_id="LicenseRef-fakeLicense-ContextAllowed-1.0"
            ),
            release_id=1,
        )
        License.objects.filter(spdx_id="LicenseRef-fakeLicense-NotAnalyzed-1.0").update(
            allowed=License.ALLOWED_ALWAYS
        )
        res = self.client.get(reverse("cube:releases-validation-5", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)

        ## Finished
        res = self.client.post(
            reverse("cube:releases-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], STEP_POLICY)
