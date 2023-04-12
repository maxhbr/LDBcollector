#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.forms import ModelForm

from cube.forms.mixins import AutocompleteFormMixin
from cube.models import Usage


class UsageForm(AutocompleteFormMixin, ModelForm):
    class Meta:
        model = Usage
        fields = [
            "version",
            "scope",
            "project",
            "linking",
            "component_modified",
            "exploitation",
        ]
        labels = {
            "version": "3rd party component and version",
        }
        autocomplete_fields = ["version"]
