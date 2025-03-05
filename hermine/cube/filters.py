#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import django_filters


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
        field_name="name", lookup_expr="icontains", label="Search in name"
    )
    search_description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains", label="Search in description"
    )
    purl_type = ValueFilter()
    programming_language = ValueFilter()
    o = django_filters.OrderingFilter(fields=("name", "usages_count"))
