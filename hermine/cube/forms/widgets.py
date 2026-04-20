#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import (
    AutocompleteMixin as AdminAutocompleteMixin,
    get_select2_language,
)
from django.urls import reverse

from cube.utils.spdx import licensing


class AutocompleteMixin(AdminAutocompleteMixin):
    def __init__(self, field, attrs=None, choices=(), using=None):
        self.field = field
        self.db = using
        self.choices = choices
        self.attrs = {} if attrs is None else attrs.copy()
        self.i18n_name = get_select2_language()

    def get_url(self):
        return reverse("autocomplete")

    @property
    def media(self):
        return super().media + forms.Media(
            css={
                "screen": ("cube/css/autocomplete.css",),
            },
        )


class SpdxIdentifierWidget(forms.Select):
    template_name = "cube/forms/widgets/spdx_identifier.html"

    def __init__(self, spdx_ids=None, attrs=None):
        if spdx_ids is None:
            spdx_ids = sorted(licensing.known_symbols.keys())
        choices = [("", "")] + [(sid, sid) for sid in spdx_ids]
        super().__init__(attrs=attrs, choices=choices)
        self.i18n_name = get_select2_language()

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.setdefault("data-tags", "true")
        attrs.setdefault("data-placeholder", "Search SPDX identifiers…")
        attrs.setdefault("data-theme", "admin-autocomplete")
        return attrs

    def optgroups(self, name, value, attrs=None):
        # Ensure LicenseRef-* values not in the static list still appear as selected
        groups = super().optgroups(name, value, attrs)
        selected_values = {
            str(v["value"])
            for group_name, subgroup, index in groups
            for v in subgroup
            if v.get("selected")
        }
        for val in value:
            if val and str(val) not in selected_values:
                self.choices = list(self.choices) + [(val, val)]
                groups = super().optgroups(name, value, attrs)
                break
        return groups

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        i18n_file = (
            ("admin/js/vendor/select2/i18n/%s.js" % self.i18n_name,)
            if self.i18n_name
            else ()
        )
        return forms.Media(
            js=(
                "admin/js/vendor/jquery/jquery%s.js" % extra,
                "admin/js/vendor/select2/select2.full%s.js" % extra,
            )
            + i18n_file
            + ("admin/js/jquery.init.js",),
            css={
                "screen": (
                    "admin/css/vendor/select2/select2%s.css" % extra,
                    "admin/css/autocomplete.css",
                    "cube/css/autocomplete.css",
                ),
            },
        )


class AutocompleteWidget(AutocompleteMixin, forms.Select):
    template_name = "cube/forms/widgets/autocomplete.html"
    pass


class AutocompleteMultipleWidget(AutocompleteMixin, forms.SelectMultiple):
    template_name = "cube/forms/widgets/autocomplete.html"
    pass
