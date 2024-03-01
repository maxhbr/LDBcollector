#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.forms import ModelForm

from cube.forms.mixins import AutocompleteFormMixin
from cube.models import LicenseCuration


class LicenseCurationCreateForm(AutocompleteFormMixin, ModelForm):
    class Meta:
        model = LicenseCuration
        fields = (
            "expression_in",
            "expression_out",
            "component",
            "version_constraint",
            "version",
            "explanation",
        )
        labels = {
            "expression_in": "Input license",
            "expression_out": "Corrected license",
        }
        autocomplete_fields = ("component", "version")


class LicenseCurationUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        component = (
            self.instance.component
            or self.instance.version
            and self.instance.version.component
        )
        if component is None:
            del self.fields["version"]
            del self.fields["version_constraint"]
            return

        self.fields["version"].queryset = component.versions.all()
        self.fields[
            "version"
        ].help_text = (
            "Select the version of the component to which the curation applies."
        )
        self.fields[
            "version"
        ].empty_label = "All versions or versions matching constraint"

    def clean(self):
        if self.instance.version is not None:
            self.instance.component = self.instance.version.component
        cleaned_data = super().clean()
        if cleaned_data.get("version") is not None:
            self.instance.component = None
        return cleaned_data

    class Meta:
        model = LicenseCuration
        fields = (
            "version_constraint",
            "version",
            "expression_in",
            "expression_out",
            "explanation",
        )
        labels = {
            "expression_in": "Input license",
            "expression_out": "Corrected license",
        }
