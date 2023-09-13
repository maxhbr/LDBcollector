#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from itertools import groupby

from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from cube.models import License, Usage, Generic, Obligation
from cube.serializers import (
    LicenseSerializer,
    SBOMSerializer,
    GenericSerializer,
    ObligationSerializer,
    GenericsAndObligationsSerializer,
    LicenseObligationSerializer,
)
from cube.utils.licenses import (
    get_licenses_triggered_obligations,
    get_license_triggered_obligations,
)


class LicenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows licenses to be viewed or edited.
    Can be filtered by SPDX ID (`?spdx_id=MIT` for example).
    """

    def get_queryset(self):
        """
        Optionally restricts the returned licences to a given spdx_id,
        by filtering against a `spdx_id` query parameter in the URL.
        """
        queryset = License.objects.all()
        spdx_id = self.request.query_params.get("spdx_id")
        if spdx_id is not None:
            queryset = queryset.filter(spdx_id=spdx_id)
        return queryset

    serializer_class = LicenseSerializer
    lookup_field = "id"


class SPDXFilter(filters.BaseInFilter, filters.ModelChoiceFilter):
    pass


class GenericFilter(filters.FilterSet):
    spdx = SPDXFilter(
        label="License SPDX id(s)",
        field_name="obligation__license__spdx_id",
        queryset=License.objects.all(),
        to_field_name="spdx_id",
    )
    exploitation = filters.ChoiceFilter(
        label="Exploitation", choices=Usage.EXPLOITATION_CHOICES, method="no_op_filter"
    )
    modification = filters.ChoiceFilter(
        label="Modification", choices=Usage.MODIFICATION_CHOICES, method="no_op_filter"
    )

    def no_op_filter(self, qs, name, value):
        return qs

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        spdx = self.form.cleaned_data.get("spdx")
        licenses = License.objects.all()
        if spdx is not None:
            licenses = licenses.filter(spdx_id__in=spdx)

        exploitation = self.form.cleaned_data.get("exploitation")
        modification = self.form.cleaned_data.get("modification")

        if exploitation or modification:
            obligations = get_licenses_triggered_obligations(
                licenses, exploitation, modification
            )
            queryset = queryset.filter(obligation__in=obligations).distinct()

        return queryset


class GenericViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows generic obligations to be viewed or edited.
    """

    queryset = Generic.objects.all()
    serializer_class = GenericSerializer
    lookup_field = "id"
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GenericFilter

    @swagger_auto_schema(
        request_body=SBOMSerializer,
        responses={200: GenericsAndObligationsSerializer()},
    )
    @action(detail=False, methods=["POST"])
    def sbom(self, request):
        """
        Get list of generic obligations for a given SBOM. Uploads a list of
        package with their licenses SPDX and return a list of generic
        obligations with packages which triggered them.
        """
        serializer = SBOMSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obligations = (
            {"obligation": obligation, "triggered_by": package["package_id"]}
            for package in serializer.validated_data["packages"]
            for spdx_id in package["spdx"]
            for obligation in get_license_triggered_obligations(
                License.objects.get(spdx_id=spdx_id),
                package["exploitation"],
                package["modification"],
            )
        )

        generics = list(
            {"generic": o["obligation"].generic, "triggered_by": o["triggered_by"]}
            for o in obligations
            if o["obligation"].generic is not None
        )

        generics_with_trigger = list()
        for generic_pk, generics_duplicates in groupby(
            sorted(generics, key=lambda g: g["generic"].pk), lambda g: g["generic"].pk
        ):
            generics_duplicates = list(generics_duplicates)
            generic = generics_duplicates[0]["generic"]
            generic.triggered_by = [g["triggered_by"] for g in generics_duplicates]
            generics_with_trigger.append(generic)

        specific_obligations = (
            o for o in obligations if o["obligation"].generic is None
        )
        obligations_with_trigger = list()
        for obligation_pk, obligations_duplicate in groupby(
            sorted(specific_obligations, key=lambda o: o["obligation"].pk),
            lambda o: o["obligation"].pk,
        ):
            obligations_duplicate = list(obligations_duplicate)
            obligation = obligations_duplicate[0]["obligation"]
            obligation.triggered_by = [o["triggered_by"] for o in obligations_duplicate]
            obligations_with_trigger.append(obligation)

        serializer = GenericsAndObligationsSerializer(
            {
                "generics": generics_with_trigger,
                "obligations": obligations_with_trigger,
            }
        )
        return Response(serializer.data)


class ObligationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows licenses to be viewed or edited
    from /obligations or /licenses/<license_id>/obligations
    """

    def get_queryset(self):
        if (license_id := self.kwargs.get("nested_1_id")) is not None:
            return Obligation.objects.filter(license__id=license_id)

        return Obligation.objects.all()

    def get_serializer_class(self):
        if self.kwargs.get("nested_1_id", None) is not None:
            return LicenseObligationSerializer
        return ObligationSerializer

    def perform_create(self, serializer):
        if (license_id := self.kwargs.get("nested_1_id")) is not None:
            serializer.save(license=License.objects.get(id=license_id))
        else:
            super().perform_create(serializer)

    def perform_update(self, serializer):
        if (license_id := self.kwargs.get("nested_1_id")) is not None:
            serializer.save(license=License.objects.get(id=license_id))
        else:
            super().perform_update(serializer)

    lookup_field = "id"
