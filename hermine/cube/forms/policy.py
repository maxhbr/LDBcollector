#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django import forms

from cube.forms.mixins import AutocompleteFormMixin
from cube.models import (
    LicenseChoice,
)


class LicenseChoiceCreateForm(AutocompleteFormMixin, forms.ModelForm):
    class Meta:
        model = LicenseChoice
        fields = "__all__"
        autocomplete_fields = ("component", "version", "product", "release")


class LicenseChoiceUpdateForm(AutocompleteFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != "expression_out" and field != "explanation":
                self.fields[field].disabled = True

    class Meta:
        model = LicenseChoice
        fields = "__all__"
        autocomplete_fields = ("component", "version", "product", "release")
