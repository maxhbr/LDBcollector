#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django import forms

from cube.forms.mixins import AutocompleteFormMixin
from cube.models import Product


class ProductForm(AutocompleteFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        autocomplete_fields = ["categories"]
        fields = "__all__"
