#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.forms import ModelForm, ModelChoiceField

from cube.models import Generic, Obligation


class ObligationGenericDiffForm(ModelForm):
    generic = ModelChoiceField(queryset=Generic.objects.all(), to_field_name="name")

    class Meta:
        model = Obligation
        fields = ("generic",)
