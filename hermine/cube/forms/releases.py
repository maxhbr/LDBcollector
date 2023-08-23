#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.forms import ModelForm

from cube.forms.mixins import AutocompleteFormMixin
from cube.models import Usage


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
            "licenses_chosen",
        ]
        labels = {
            "version": "3rd party component and version",
        }
        autocomplete_fields = ["version", "licenses_chosen"]
