#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django import forms

from cube.forms.mixins import AutocompleteFormMixin
from cube.models import Product, Category


class ProductForm(AutocompleteFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        autocomplete_fields = ["categories", "outbound_licenses"]
        fields = "__all__"


class CategoryForm(AutocompleteFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        autocomplete_fields = ["outbound_licenses"]
        fields = "__all__"
