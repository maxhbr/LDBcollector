#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.test import TestCase
from django.urls import reverse

from cube.forms.importers import ImportBomForm
from cube.models import Usage


class ImportForm(TestCase):
    fixtures = ["test_data.json"]

    def test_import_bom_form_with_spdx(self):
        url = reverse("cube:release_bom", kwargs={"release_pk": 1})
        self.client.post(
            url,
            {
                "bom_type": ImportBomForm.BOM_SPDX,
                "import_mode": ImportBomForm.IMPORT_MODE_REPLACE,
                "linking": Usage.LINKING_DYNAMIC,
                "file": open("cube/fixtures/fake_sbom.json", "r"),
            },
        )
