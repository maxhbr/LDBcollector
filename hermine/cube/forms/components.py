#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.forms import ModelForm

from cube.models import LicenseCuration


class LicenseCurationCreateForm(ModelForm):
    class Meta:
        model = LicenseCuration
        fields = (
            "expression_in",
            "expression_out",
            "component",
            "version",
            "explanation",
        )
        labels = {
            "expression_in": "Input license",
            "expression_out": "Corrected license",
        }


class LicenseCurationUpdateForm(ModelForm):
    class Meta:
        model = LicenseCuration
        fields = (
            "expression_in",
            "expression_out",
            "explanation",
        )
        labels = {
            "expression_in": "Input license",
            "expression_out": "Corrected license",
        }
