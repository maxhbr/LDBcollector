# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django import forms
from .models import Release


class ImportGenericsForm(forms.Form):
    file = forms.FileField(label="Import a JSON containing Generic Obligations")


class ImportLicensesForm(forms.Form):
    file = forms.FileField(label="Upload a JSON containing license data")


class ImportBomForm(forms.ModelForm):
    BOM_ORT = "ORTBom"
    BOM_SPDX = "SPDXBom"
    BOM_CHOICES = (
        (BOM_ORT, "ORT Bill of Materials"),
        (BOM_SPDX, "SPDX Bill of Materials"),
    )
    bom_type = forms.ChoiceField(label="File format", choices=BOM_CHOICES)
    file = forms.FileField()

    class Meta:
        model = Release
        fields = "bom_type", "file"
