# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.test import TestCase

from cube.importers import import_spdx_file
from cube.models import Generic, Usage, LINKING_PACKAGE, License
from cube.utils.generics import export_generics, handle_generics_json
from cube.utils.licenses import (
    create_or_update_license,
    export_licenses,
    handle_licenses_json,
)


class ImportLicensesTestCase(TestCase):
    fixtures = ["test_data.json"]

    def test_export_import(self):
        count = License.objects.all().count()
        export = export_licenses(indent=True)
        License.objects.all().delete()
        handle_licenses_json(export)
        self.assertEqual(License.objects.all().count(), count)

    def test_generic_autocreation(self):
        json = [
            {
                "id": 1,
                "spdx_id": "lorem license",
                "long_name": "Lorem License",
                "color": "Green",
                "foss": "Yes",
                "comment": "Open Source",
                "obligation_set": [
                    {
                        "id": 1,
                        "generic_name": "Generic Obligation 1",
                        "name": "License 1 obligation 1",
                        "verbatim": "Long text.",
                        "passivity": "Active",
                        "trigger_expl": "DistributionSource",
                        "trigger_mdf": "AlteredUnmodified",
                        "generic": 1,
                    },
                    {
                        "id": 2,
                        "generic_name": "Generic Obligation 2",
                        "name": "License 1 obligation 2",
                        "verbatim": "Long text.",
                        "passivity": "Active",
                        "trigger_expl": "DistributionSource",
                        "trigger_mdf": "AlteredUnmodified",
                        "generic": 2,
                    },
                ],
            },
            {
                "id": 2,
                "spdx_id": "lorem-license-2",
                "long_name": "Lorem License 2",
                "color": "Green",
                "foss": "Yes",
                "comment": "Open Source",
                "obligation_set": [
                    {
                        "id": 3,
                        "generic_name": "Generic Obligation 1",
                        "name": "License 2 obligation 1",
                        "verbatim": "Long text.",
                        "passivity": "Active",
                        "trigger_expl": "DistributionSource",
                        "trigger_mdf": "AlteredUnmodified",
                        "generic": 1,
                    }
                ],
            },
        ]

        for license in json:
            create_or_update_license(license)

        self.assertEqual(Generic.objects.all().count(), 2)


class ImportGenericTestCase(TestCase):
    fixtures = ["test_data.json"]

    def test_export_import(self):
        count = Generic.objects.all().count()
        export = export_generics(indent=True)
        Generic.objects.all().delete()
        handle_generics_json(export)
        self.assertEqual(License.objects.all().count(), count)


class ImportSBOMTestCase(TestCase):
    fixtures = ["test_data.json"]

    def test_import_spdx_file(self):
        with open("../testfiles/venom_short.spdx.yaml") as f:
            import_spdx_file(f, 1, defaults={"linking": LINKING_PACKAGE})
        usage = Usage.objects.get(
            version__component__name="github.com/gorilla/websocket",
            version__version_number="v1.4.2",
        )
        self.assertEqual(
            usage.release.pk,
            1,
        )
        self.assertEqual(usage.linking, LINKING_PACKAGE)

        with open("../testfiles/venom_short.spdx.yaml") as f:
            import_spdx_file(f, 1, replace=False)
        new_usage = Usage.objects.get(
            version__component__name="github.com/gorilla/websocket",
            version__version_number="v1.4.2",
        )
        self.assertEqual(
            usage.pk,
            new_usage.pk,
        )

        with open("../testfiles/venom_short.spdx.yaml") as f:
            import_spdx_file(f, 1, replace=True)
        new_usage = Usage.objects.get(
            version__component__name="github.com/gorilla/websocket",
            version__version_number="v1.4.2",
        )
        self.assertNotEqual(
            usage.pk,
            new_usage.pk,
        )
