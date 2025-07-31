#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import django_filters
from django.db.models import Q
from django_filters.constants import EMPTY_VALUES


class ValueFilter(django_filters.ChoiceFilter):
    @property
    def field(self):
        qs = (
            self.parent.queryset.order_by(self.field_name)
            .values_list(self.field_name, flat=True)
            .distinct()
        )
        self.extra["choices"] = [(o, o) for o in qs]
        return super().field


class MultiFieldSearchFilter(django_filters.CharFilter):
    fields: list[str]

    def __init__(self, fields=None, *args, **kwargs):
        if fields is not None:
            self.fields = fields
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        query = Q()
        for field in self.fields:
            query |= Q(**{f"{field}__icontains": value})
        return qs.filter(query)


class ComponentOrVersionFilter(django_filters.CharFilter):
    fields = ("component__name", "version__component__name")


class ReleaseBomFilter(
    django_filters.FilterSet,
):
    search = django_filters.CharFilter(
        field_name="version__purl", lookup_expr="icontains", label="Search"
    )
    license_expression = ValueFilter()
    project = ValueFilter()
    scope = ValueFilter()
    o = django_filters.OrderingFilter(
        fields=("project", "scope", "exploitation", "license_expression")
    )


class LicenseFilter(
    django_filters.FilterSet,
):
    search = MultiFieldSearchFilter(fields=("spdx_id", "long_name"), label="Search")
    copyleft = ValueFilter()
    patent_grant = ValueFilter()
    policy__allowed = ValueFilter()
    policy__status = ValueFilter()
    o = django_filters.OrderingFilter(fields=("spdx_id", "policy__allowed"))


class LicenseCurationFilter(
    django_filters.FilterSet,
):
    search_component = ComponentOrVersionFilter(label="Component")
    search_expression_in = django_filters.CharFilter(
        field_name="expression_in", lookup_expr="icontains", label="Stated license"
    )
    search_expression_out = django_filters.CharFilter(
        field_name="expression_out", lookup_expr="icontains", label="Corrected license"
    )


class ComponentFilter(
    django_filters.FilterSet,
):
    search = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Name"
    )
    search_description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains", label="Description"
    )
    purl_type = ValueFilter()
    programming_language = ValueFilter()
    o = django_filters.OrderingFilter(fields=("name", "usages_count"))


class DerogationFilter(django_filters.FilterSet):
    search_license = MultiFieldSearchFilter(
        fields=("license__spdx_id", "license__long_name"), label="License"
    )
    search_component = ComponentOrVersionFilter(label="Component")
    scope = ValueFilter()
    linking = ValueFilter()
    modification = ValueFilter()
    exploitation = ValueFilter()


class LicenseChoiceFilter(django_filters.FilterSet):
    search_expression_in = django_filters.CharFilter(
        field_name="expression_in", lookup_expr="icontains", label="License expression"
    )
    search_expression_out = django_filters.CharFilter(
        field_name="expression_out", lookup_expr="icontains", label="Choice"
    )
