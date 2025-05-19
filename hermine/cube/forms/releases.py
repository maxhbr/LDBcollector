#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.forms import ModelForm, DateTimeInput

from cube.forms.mixins import AutocompleteFormMixin
from cube.models import Usage, Release


class ReleaseForm(AutocompleteFormMixin, ModelForm):
    class Meta:
        model = Release
        fields = [
            "product",
            "release_number",
            "commit",
            "ship_status",
            "pub_date",
            "outbound_licenses",
        ]
        autocomplete_fields = ["outbound_licenses"]
        widgets = {
            "pub_date": DateTimeInput(
                attrs={"type": "datetime-local", "style": "max-width: 220px;"}
            ),
        }


class UsageForm(AutocompleteFormMixin, ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show the version field if we are creating a new usage
        if kwargs["instance"] is not None:
            del self.fields["version"]

    class Meta:
        model = Usage
        fields = [
            "version",
            "scope",
            "project",
            "linking",
            "component_modified",
            "exploitation",
            "description",
            "license_expression",
        ]
        labels = {
            "version": "3rd party component and version",
        }
        autocomplete_fields = ["version"]
