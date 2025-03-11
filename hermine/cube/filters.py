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


class ComponentOrVersionFilter(django_filters.CharFilter):
    def __init__(self):
        super().__init__(label="Component")

    def filter(self, qs, value: str):
        if value in EMPTY_VALUES:
            return qs
        return self.filter(
            Q(component__name__icontains=value) | Q(version__component__icontains=value)
        )


class ReleaseBomFilter(
    django_filters.FilterSet,
):
    search = django_filters.CharFilter(
        field_name="version__purl", lookup_expr="icontains", label="Search"
    )
    project = ValueFilter()
    scope = ValueFilter()
    o = django_filters.OrderingFilter(
        fields=("project", "scope", "exploitation", "license_expression")
    )


class LicenseFilter(
    django_filters.FilterSet,
):
    search = django_filters.CharFilter(
        field_name="long_name", lookup_expr="icontains", label="Search"
    )
    copyleft = ValueFilter()
    patent_grant = ValueFilter()
    policy__allowed = ValueFilter()
    policy__status = ValueFilter()
    o = django_filters.OrderingFilter(fields=("spdx_id", "policy__allowed"))


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
    search_license = django_filters.CharFilter(
        field_name="license__spdx_id", lookup_expr="icontains", label="License SPDX"
    )
    category = ValueFilter(label="Product category")
    search = ComponentOrVersionFilter()
    scope = ValueFilter()
    linking = ValueFilter()
    modification = ValueFilter()
    exploitation = ValueFilter()
