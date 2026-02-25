#  SPDX-FileCopyrightText: 2026 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from cube.forms.widgets import AutocompleteWidget, AutocompleteMultipleWidget


class FieldsetFormMixin:
    fieldsets = []

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.template_name = "django/forms/fieldset_field.html"

    @property
    def template_name(self):
        return "django/forms/fieldset.html"

    def get_context(self):
        context = super().get_context()
        fields_by_name = {bf.name: (bf, errors) for bf, errors in context["fields"]}
        fieldset_groups = []
        used = set()
        for title, opts in self.fieldsets:
            group_fields = []
            collapsible = []
            for name in opts["fields"]:
                if isinstance(name, tuple):
                    section_title, section_fields = name
                    section_items = []
                    for sname in section_fields:
                        if sname in fields_by_name:
                            section_items.append(fields_by_name[sname])
                            used.add(sname)
                    if section_items:
                        collapsible.append((section_title, section_items))
                elif name in fields_by_name:
                    group_fields.append(fields_by_name[name])
                    used.add(name)
            fieldset_groups.append((title, group_fields, collapsible))

        orphan_fields = [
            (bf, errors) for bf, errors in context["fields"] if bf.name not in used
        ]
        if orphan_fields:
            fieldset_groups.append(("", orphan_fields, []))

        context["fieldset_groups"] = fieldset_groups
        return context


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
