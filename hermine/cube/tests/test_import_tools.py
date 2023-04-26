# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from cube.importers import import_spdx_file
from cube.models import Generic, Usage, License, Team, Obligation
from cube.utils.generics import export_generics, handle_generics_json
from cube.utils.licenses import (
    export_licenses,
    handle_licenses_json,
)
from .mixins import ForceLoginMixin


class ImportLicensesTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_export_import_after_delete(self):
        count = License.objects.all().count()
        obligations_counts = {
            lic.spdx_id: lic.obligation_set.count() for lic in License.objects.all()
        }
        export = export_licenses(indent=True)
        License.objects.all().delete()
        Obligation.objects.all().delete()
        handle_licenses_json(export)
        self.assertEqual(License.objects.all().count(), count)
        for lic in License.objects.all():
            self.assertEqual(
                lic.obligation_set.count(), obligations_counts[lic.spdx_id]
            )

    def test_export_import_pages(self):
        res = self.client.get(reverse("cube:export_licenses"))
        self.assertEqual(res.status_code, 200)
        License.objects.all().delete()
        res = self.client.post(
            reverse("cube:licenses"),
            data={
                "file": SimpleUploadedFile(
                    "lincenses.json", res.content, "application/json"
                )
            },
        )
        self.assertRedirects(res, reverse("cube:licenses"))

    def test_generic_autocreation(self):
        self.assertEqual(Generic.objects.all().count(), 1)
        data = [
            {
                "model": "cube.license",
                "fields": {
                    "spdx_id": "lorem license",
                    "long_name": "Lorem License",
                    "allowed": "always",
                    "foss": "Yes",
                    "comment": "Open Source",
                },
            },
            {
                "model": "cube.license",
                "fields": {
                    "spdx_id": "lorem-license-2",
                    "long_name": "Lorem License 2",
                    "allowed": "always",
                    "foss": "Yes",
                    "comment": "Open Source",
                },
            },
            {
                "model": "cube.obligation",
                "fields": {
                    "license": ["lorem license"],
                    "generic": ["Generic Obligation 1"],
                    "name": "License 1 obligation 1",
                    "verbatim": "Long text.",
                    "passivity": "Active",
                    "trigger_expl": "DistributionSource",
                    "trigger_mdf": "AlteredUnmodified",
                },
            },
            {
                "model": "cube.obligation",
                "fields": {
                    "license": ["lorem license"],
                    "generic": ["Generic Obligation 2"],
                    "name": "License 1 obligation 2",
                    "verbatim": "Long text.",
                    "passivity": "Active",
                    "trigger_expl": "DistributionSource",
                    "trigger_mdf": "AlteredUnmodified",
                },
            },
            {
                "model": "cube.obligation",
                "fields": {
                    "license": ["lorem-license-2"],
                    "generic": ["Generic Obligation 1"],
                    "name": "License 2 obligation 1",
                    "verbatim": "Long text.",
                    "passivity": "Active",
                    "trigger_expl": "DistributionSource",
                    "trigger_mdf": "AlteredUnmodified",
                },
            },
        ]

        handle_licenses_json(json.dumps(data))
        self.assertEqual(Generic.objects.all().count(), 3)


class ImportGenericTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_export_import(self):
        count = Generic.objects.all().count()
        team_count = Team.objects.all().count()
        export = export_generics(indent=True)
        Generic.objects.all().delete()
        Team.objects.all().delete()
        handle_generics_json(export)
        self.assertEqual(Generic.objects.all().count(), count)
        self.assertEqual(Team.objects.all().count(), team_count)
        # test importing twice is idempotent
        handle_generics_json(export)
        self.assertEqual(Generic.objects.all().count(), count)

    def test_export_import_pages(self):
        res = self.client.get(reverse("cube:export_generics"))
        self.assertEqual(res.status_code, 200)
        Generic.objects.all().delete()
        res = self.client.post(
            reverse("cube:generics"),
            data={
                "file": SimpleUploadedFile(
                    "generics.json", res.content, "application/json"
                )
            },
        )
        self.assertRedirects(res, reverse("cube:generics"))


class ImportSBOMTestCase(TestCase):
    fixtures = ["test_data.json"]

    def test_import_sbom_linking_and_replace(self):
        with open("cube/fixtures/fake_sbom.json") as f:
            import_spdx_file(f, 1, linking=Usage.LINKING_DYNAMIC)
        usage = Usage.objects.get(
            version__component__name="spdx-valid-dependency",
            version__version_number="v1",
        )
        self.assertEqual(
            usage.release.pk,
            1,
        )
        self.assertEqual(usage.linking, Usage.LINKING_DYNAMIC)

        with open("cube/fixtures/fake_sbom.json") as f:
            import_spdx_file(f, 1, replace=False)
        new_usage = Usage.objects.get(
            version__component__name="spdx-valid-dependency",
            version__version_number="v1",
        )
        self.assertEqual(
            usage.pk,
            new_usage.pk,
        )

        with open("cube/fixtures/fake_sbom.json") as f:
            import_spdx_file(f, 1, replace=True)
        new_usage = Usage.objects.get(
            version__component__name="spdx-valid-dependency",
            version__version_number="v1",
        )
        self.assertNotEqual(
            usage.pk,
            new_usage.pk,
        )
