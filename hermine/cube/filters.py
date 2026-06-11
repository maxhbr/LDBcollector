#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import django_filters
from django.db.models import Q
from django_filters.constants import EMPTY_VALUES

from cube.models import License


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


class ComponentOrVersionFilter(MultiFieldSearchFilter):
    fields = ("component__name", "version__component__name")


class FilterSet(django_filters.FilterSet):
    @property
    def collapsible_fields(self):
        return getattr(getattr(self, "Meta", {}), "collapsible_fields", [])


class ReleaseBomFilter(FilterSet):
    search = django_filters.CharFilter(
        field_name="version__purl", lookup_expr="icontains", label="Search"
    )
    license_expression = ValueFilter()
    project = ValueFilter()
    scope = ValueFilter()
    o = django_filters.OrderingFilter(
        fields=("project", "scope", "exploitation", "license_expression")
    )


class LicenseFilter(FilterSet):
    search = MultiFieldSearchFilter(fields=("spdx_id", "long_name"), label="Search")
    copyleft = ValueFilter()
    policy__status = ValueFilter(label="Review status")
    o = django_filters.OrderingFilter(
        label="Sort by",
        choices=(
            ("long_name", "Alphabetical order (A-Z)"),
            ("-long_name", "Alphabetical order (Z-A)"),
            ("-created", "Recently added"),
        ),
        fields=("long_name", "created"),
        field_labels={"long_name": "Alphabetical order", "created": "Recently added"},
    )

    patent_grant = ValueFilter()
    policy__allowed = ValueFilter()

    class Meta:
        model = License
        fields = [
            "search",
            "o",
            "policy__status",
            "copyleft",
            "policy__allowed",
            "patent_grant",
        ]
        collapsible_fields = ["policy__allowed", "patent_grant"]


class LicenseCurationFilter(
    FilterSet,
):
    search_component = ComponentOrVersionFilter(label="Component")
    search_expression_in = django_filters.CharFilter(
        field_name="expression_in", lookup_expr="icontains", label="Stated license"
    )
    search_expression_out = django_filters.CharFilter(
        field_name="expression_out", lookup_expr="icontains", label="Corrected license"
    )


class ComponentFilter(
    FilterSet,
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


class DerogationFilter(FilterSet):
    search_license = MultiFieldSearchFilter(
        fields=("license__spdx_id", "license__long_name"), label="License"
    )
    search_component = ComponentOrVersionFilter(label="Component")
    scope = ValueFilter()
    linking = ValueFilter()
    modification = ValueFilter()
    exploitation = ValueFilter()


class ObligationByGenericFilter(FilterSet):
    search = django_filters.CharFilter(
        field_name="license__spdx_id",
        lookup_expr="icontains",
        label="Search for a license",
    )
    copyleft = ValueFilter(field_name="license__copyleft", label="Copyleft type")
    o = django_filters.OrderingFilter(
        fields=(("license__long_name", "license"),),
        choices=(
            ("license__long_name", "Alphabetical order (A-Z)"),
            ("-license__long_name", "Alphabetical order (Z-A)"),
        ),
        label="Sort by (license)",
    )


class LicenseChoiceFilter(FilterSet):
    search_expression_in = django_filters.CharFilter(
        field_name="expression_in", lookup_expr="icontains", label="License expression"
    )
    search_expression_out = django_filters.CharFilter(
        field_name="expression_out", lookup_expr="icontains", label="Choice"
    )
