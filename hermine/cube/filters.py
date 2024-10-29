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
