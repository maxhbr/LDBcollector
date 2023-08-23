#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django import forms
from django.contrib.admin.widgets import (
    AutocompleteMixin as AdminAutocompleteMixin,
    get_select2_language,
)
from django.urls import reverse


class AutocompleteMixin(AdminAutocompleteMixin):
    def __init__(self, field, attrs=None, choices=(), using=None):
        self.field = field
        self.db = using
        self.choices = choices
        self.attrs = {} if attrs is None else attrs.copy()
        self.i18n_name = get_select2_language()

    def get_url(self):
        return reverse("admin:autocomplete")

    @property
    def media(self):
        return super().media + forms.Media(
            css={
                "screen": ("cube/css/autocomplete.css",),
            },
        )


class AutocompleteWidget(AutocompleteMixin, forms.Select):
    pass


class AutocompleteMultipleWidget(AutocompleteMixin, forms.SelectMultiple):
    pass
