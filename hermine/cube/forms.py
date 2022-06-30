# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django import forms
from .models import Release, LINKING_CHOICES


class ImportGenericsForm(forms.Form):
    file = forms.FileField()


class ImportLicensesForm(forms.Form):
    file = forms.FileField()


class ImportBomForm(forms.ModelForm):
    BOM_ORT = "ORTBom"
    BOM_SPDX = "SPDXBom"
    BOM_CHOICES = (
        (BOM_ORT, "ORT Evaluated model"),
        (BOM_SPDX, "SPDX Bill of Materials"),
    )
    IMPORT_MODE_MERGE = "Merge"
    IMPORT_MODE_REPLACE = "Replace"
    IMPORT_MODE_CHOICES = (
        (IMPORT_MODE_REPLACE, "Replace all currently saved component usages"),
        (IMPORT_MODE_MERGE, "Add new component usages while keeping previous ones"),
    )
    bom_type = forms.ChoiceField(label="File format", choices=BOM_CHOICES)
    file = forms.FileField()
    import_mode = forms.ChoiceField(
        choices=IMPORT_MODE_CHOICES, widget=forms.RadioSelect
    )
    linking = forms.ChoiceField(
        choices=((None, "---"), *LINKING_CHOICES),
        required=False,
        initial=None,
        label="Components linking",
    )

    class Meta:
        model = Release
        fields = "bom_type", "file"
