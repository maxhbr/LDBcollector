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


def import_licenses():
    with open("cube/fixtures/fake_licenses.json") as licenses_file:
        handle_licenses_json(licenses_file.read())


class ReleaseStepsAPITestCase(BaseHermineAPITestCase):
    def import_sbom(self):
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

    def test_valid(self):
        self.create_product()
        self.create_release()
        import_licenses()
        License.objects.create(
            spdx_id="LicenseRef-fakeLicense-NotAnalyzed-1.0",
            allowed=License.ALLOWED_ALWAYS,
        )

        self.create_curations()
        self.create_ands_corrections()
        self.create_exploitations()
        self.create_choices()
        self.create_derogations()

        self.import_sbom()
        res = self.client.post(
            reverse("cube:releases-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], STEP_POLICY)

    def test_step_by_step(self):
        self.create_product()
        self.create_release()
        self.import_sbom()

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

        self.create_curations()
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
        import_licenses()
        res = self.client.get(reverse("cube:releases-validation-2", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)

        self.create_ands_corrections()
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

        self.create_exploitations()
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

        self.create_choices()
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
        self.client.post(reverse("cube:releases-update-validation", kwargs={"id": 1}))
        res = self.client.get(reverse("cube:releases-validation-5", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], False)
        self.assertEqual(
            len(res.data["usages_lic_unknown"]), 1
        )  # wrong-concluded-dependency
        self.assertEqual(
            len(res.data["usages_lic_context_allowed"]), 1
        )  # spdx-valid-dependency

        self.create_derogations()
        res = self.client.get(reverse("cube:releases-validation-5", kwargs={"id": 1}))
        self.assertEqual(res.data["valid"], True)

        ## Finished
        res = self.client.post(
            reverse("cube:releases-update-validation", kwargs={"id": 1})
        )
        self.assertEqual(res.data["validation_step"], STEP_POLICY)

    def create_curations(self):
        # Licenses with no concluded license
        LicenseCuration.objects.create(
            expression_in="Allowed-1.0 AND ContextAllowed-1.0",
            expression_out="LicenseRef-fakeLicense-Allowed-1.0 OR LicenseRef-fakeLicense-ContextAllowed-1.0",
        )
        LicenseCuration.objects.create(
            component=Component.objects.get_or_create(name="no-assertion-dependency")[
                0
            ],
            expression_in="NOASSERTION",
            expression_out="LicenseRef-fakeLicense-Allowed-1.0",
        )
        # Licenses with wrong concluded licenses
        LicenseCuration.objects.create(
            component=Component.objects.get_or_create(
                name="wrong-concluded-dependency"
            )[0],
            expression_in="LicenseRef-fakeLicense-ContextAllowed-1.0",
            expression_out="LicenseRef-fakeLicense-Allowed-1.0 AND LicenseRef-fakeLicense-NotAnalyzed-1.0",
        )

    def create_ands_corrections(self):
        LicenseCuration.objects.create(
            expression_in="LicenseRef-fakeLicense-Allowed-1.0 AND LicenseRef-fakeLicense-ContextAllowed-1.0",
            expression_out="LicenseRef-fakeLicense-Allowed-1.0 OR LicenseRef-fakeLicense-ContextAllowed-1.0",
        )

    def create_exploitations(self):
        Exploitation.objects.create(
            release_id=1,
            scope=Usage.DEFAULT_SCOPE,
            project=Usage.DEFAULT_PROJECT,
            exploitation=Usage.EXPLOITATION_INTERNAL,
        )

    def create_choices(self):
        self.client.post(
            reverse("cube:choices-list"),
            data={
                "expression_in": "LicenseRef-fakeLicense-Allowed-1.0 OR LicenseRef-fakeLicense-ContextAllowed-1.0",
                "expression_out": "LicenseRef-fakeLicense-Allowed-1.0",
            },
        )

    def create_derogations(self):
        Derogation.objects.create(
            license=License.objects.get(
                spdx_id="LicenseRef-fakeLicense-ContextAllowed-1.0"
            ),
            release_id=1,
        )
        allowed_license = License.objects.get(
            spdx_id="LicenseRef-fakeLicense-NotAnalyzed-1.0"
        )
        allowed_license.allowed = License.ALLOWED_ALWAYS
        allowed_license.save()
