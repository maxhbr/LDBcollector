#  SPDX-FileCopyrightText: 2025 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django import forms
from django.forms import ModelForm

from cube.models import Token


class APITokenForm(ModelForm):
    class Meta:
        model = Token
        fields = ["description", "key", "ttl"]
        widgets = {
            "description": forms.TextInput,
            "key": forms.TextInput(attrs={"readonly": "readonly"}),
        }
