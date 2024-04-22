#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from cube.forms.widgets import AutocompleteWidget, AutocompleteMultipleWidget


class AutocompleteFormMixin:
    def __init_subclass__(cls, **kwargs):
        for field in cls.Meta.autocomplete_fields:
            cls.Meta.widgets = getattr(cls.Meta, "widgets", {})
            if cls.Meta.model._meta.get_field(field).many_to_many:
                cls.Meta.widgets[field] = AutocompleteMultipleWidget(
                    cls.Meta.model._meta.get_field(field)
                )
            else:
                cls.Meta.widgets[field] = AutocompleteWidget(
                    cls.Meta.model._meta.get_field(field)
                )

        super().__init_subclass__(**kwargs)
