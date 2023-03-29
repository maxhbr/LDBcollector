#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from cube.forms.widgets import AutocompleteWidget


class AutocompleteFormMixin:
    def __init_subclass__(cls, **kwargs):
        for field in cls.Meta.autocomplete_fields:
            cls.Meta.widgets = getattr(cls.Meta, "widgets", {})
            cls.Meta.widgets[field] = AutocompleteWidget(
                cls.Meta.model._meta.get_field(field)
            )
        super().__init_subclass__(**kwargs)
