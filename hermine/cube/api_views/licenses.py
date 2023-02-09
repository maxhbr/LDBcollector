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
)
from cube.utils.licenses import (
    get_licenses_triggered_obligations,
    get_license_triggered_obligations,
)


class LicenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows licenses to be viewed or edited.
    """

    queryset = License.objects.all()
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
        responses={200: GenericSerializer(many=True)},
    )
    @action(detail=False, methods=["POST"])
    def sbom(self, request):
        """
        Get list of generic obligations for a given SBOM.

        Uploads a list of package with their licenses SPDX and return a list of
        generic obligations with packages which triggered them.
        """
        serializer = SBOMSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        generics = (
            {"generic": generic, "triggered_by": package["package_id"]}
            for package in serializer.validated_data["packages"]
            for generic in Generic.objects.filter(
                obligation__in=get_license_triggered_obligations(
                    License.objects.get(spdx_id=package["spdx"]),
                    package["exploitation"],
                    package["modification"],
                )
            ).distinct()
        )

        sort_key = lambda generic: generic["generic"].pk
        sorted_generics = groupby(sorted(generics, key=sort_key), sort_key)
        serializer_data = list()
        for generic_pk, generics in sorted_generics:
            generics = list(generics)
            generic = generics[0]["generic"]
            generic.triggered_by = [g["triggered_by"] for g in generics]
            serializer_data.append(generic)

        serializer = self.get_serializer(
            serializer_data,
            many=True,
        )
        return Response(serializer.data)


class ObligationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows licenses to be viewed or edited.
    """

    def get_queryset(self):
        """
        Handles if the user is accessing the viewset from root of api or from a nested
        obligationset in a license


        :return: [description]
        :rtype: [type]
        """
        license = self.kwargs.get("id_id")
        return (
            Obligation.objects.all()
            if license is None
            else Obligation.objects.filter(license__id=license)
        )

    serializer_class = ObligationSerializer
    lookup_field = "id"
