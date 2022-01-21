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


class ImportBomForm(forms.Form):
    BOM_CHOICES = (
        ("ORTBom", "ORT Bill of Materials"),
        ("SPDXBom", "SPDX Bill of Materials"),
    )
    bom_type = forms.ChoiceField(
        label="Produit et version concernée", choices=BOM_CHOICES
    )
    release = forms.ModelChoiceField(
        label="Produit et version concernée", queryset=Release.objects.all()
    )
    file = forms.FileField()
