# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.test import TestCase

from cube.models import Generic
from cube.utils.licenses import create_or_update_license


class ImportLicensesTestCase(TestCase):
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
