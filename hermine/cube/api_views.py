# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from itertools import groupby

from django.http import HttpResponse
from django.urls import reverse
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from junit_xml import TestCase, TestSuite, to_xml_report_string
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.routers import APIRootView

from cube.serializers import (
    LicenseSerializer,
    ObligationSerializer,
    GenericSerializer,
    UsageSerializer,
    ProductSerializer,
    ReleaseSerializer,
    ComponentSerializer,
    VersionSerializer,
    UploadSPDXSerializer,
    UploadORTSerializer,
    SBOMSerializer,
    LicenseChoiceSerializer,
    Validation1Serializer,
    Validation2Serializer,
    Validation3Serializer,
    Validation4Serializer,
    Validation5Serializer,
)
from .importers import import_ort_evaluated_model_json_file, import_spdx_file
from .models import (
    Product,
    Release,
    Usage,
    License,
    Obligation,
    Generic,
    Component,
    Version,
    LicenseChoice,
)
from .utils.licenses import (
    get_usages_obligations,
    get_license_triggered_obligations,
    get_licenses_triggered_obligations,
)
from .utils.releases import (
    update_validation_step,
    validate_step_1,
    validate_step_2,
    validate_step_4,
    validate_step_5,
    validate_step_3,
)


class RootView(APIRootView):
    """Documentation for the API is available through Swagger at /api-doc"""

    pass


class LicenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows licenses to be viewed or edited.
    """

    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    lookup_field = "id"


class UsageViewSet(viewsets.ModelViewSet):
    queryset = Usage.objects.all()
    serializer_class = UsageSerializer


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

    @action(detail=False, methods=["POST"])
    def sbom(self, request):
        """
        Get list of generic obligations for a given SBOM.

        Uploads a list of package with their licenses SPDX and return a list of generic obligations with
        packages which triggered them.
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


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"


class ReleaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows releases to be viewed or edited, and to check validation steps.
    """

    serializer_class = ReleaseSerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        Handles if the user is accessing the viewset from root of api or from a nested
        # ReleaseSet in a product (api/products/<int:product_id>/releases)

        :return: Set of Release objects
        :rtype: QuerySet
        """
        # This kwargs should be id, not name_id

        product_id = self.kwargs.get("name_id")
        if product_id is None:
            response = Release.objects.all()
        else:
            response = Release.objects.filter(product__id=product_id)

        return response

    @action(detail=True, methods=["post"])
    def update_validation(self, pk, **kwargs):
        """
        Recalculate validation step of the release
        """
        release = self.get_object()
        update_validation_step(release)

        return Response(self.get_serializer_class()(release).data)

    @swagger_auto_schema(
        responses={200: Validation1Serializer},
    )
    @action(detail=True, methods=["get"])
    def validation_1(self, request, **kwargs):
        """
        Check for licenses that haven't been normalized.
        """
        response = {}
        release = self.get_object()

        response["valid"], context = validate_step_1(release)
        response["unnormalized_usages"] = context["unnormalized_usages"]
        response["details"] = reverse("cube:release_detail", kwargs={"pk": release.pk})

        return Response(Validation1Serializer(response).data)

    @swagger_auto_schema(
        responses={200: Validation2Serializer},
    )
    @action(detail=True, methods=["get"])
    def validation_2(self, request, **kwargs):
        """
        Check that all the licences in a release have been created and checked.
        """
        response = {}
        release = self.get_object()

        response["valid"], context = validate_step_2(release)
        response.update(context)
        response["details"] = reverse("cube:release_detail", kwargs={"pk": release.pk})

        return Response(Validation2Serializer(response).data)

    @swagger_auto_schema(
        responses={200: Validation3Serializer},
    )
    @action(detail=True, methods=["get"])
    def validation_3(self, request, **kwargs):
        """
        Confirm ANDs operators in SPDX expressions are not poorly registered ORs.
        """
        response = {}
        release = self.get_object()

        response["valid"], context = validate_step_3(release)
        response["to_confirm"] = context["to_confirm"]
        response["details"] = reverse("cube:release_detail", kwargs={"pk": release.pk})

        return Response(Validation3Serializer(response).data)

    @swagger_auto_schema(
        responses={200: Validation4Serializer},
    )
    @action(detail=True, methods=["get"])
    def validation_4(self, request, **kwargs):
        """
        Check all licenses choices are done.
        """
        response = {}
        release = self.get_object()

        response["valid"], context = validate_step_4(release)
        response.update(context)
        response["details"] = reverse("cube:release_detail", kwargs={"pk": release.pk})

        return Response(Validation4Serializer(response).data)

    @swagger_auto_schema(
        responses={200: Validation5Serializer},
    )
    @action(detail=True, methods=["get"])
    def validation_5(self, request, **kwargs):
        """
        Check that the licences are compatible with policy.
        """
        response = {}
        release = self.get_object()

        response["valid"], context = validate_step_5(release)
        response.update(context)
        response["details"] = reverse("cube:release_detail", kwargs={"pk": release.pk})

        return Response(Validation5Serializer(response).data)

    @action(
        detail=True,
        methods=["get"],
    )
    def junit(self, request, **kwargs):
        release = self.get_object()

        step1 = TestCase(
            "Usage normalization",
        )
        valid, context = validate_step_1(release)
        if not valid:
            step1.add_failure_info(
                message=f"{len(context['unnormalized_usages'])} usages are not normalized/"
            )

        step2 = TestCase("Licenses")
        valid, context = validate_step_2(release)
        if not valid:
            if len(context["licenses_to_check"]) > 0:
                step2.add_failure_info(
                    message=f"{len(context['licenses_to_check'])} licenses must be checked"
                )
            if len(context["licenses_to_create"]) > 0:
                step2.add_failure_info(
                    message=f"{len(context['licenses_to_create'])} licenses must be created"
                )

        step4 = TestCase("License choices")
        valid, context = validate_step_4(release)
        if not valid:
            step4.add_failure_info(
                f"{len(context['to_resolve'])} licenses choices to resolve"
            )

        step5 = TestCase("Policy compatibility")
        valid, context = validate_step_5(release)
        if not valid:
            count = (
                len(context["usages_lic_red"])
                + len(context["usages_lic_orange"])
                + len(context["usages_lic_grey"])
            )
            step5.add_failure_info(f"{count} invalid component usages")

        ts = TestSuite(
            f"{release} Hermine validation steps", [step1, step2, step4, step5]
        )

        return HttpResponse(
            content=to_xml_report_string([ts]), content_type="application/xml"
        )

    @action(detail=True, methods=["get"])
    def obligations(self, pk, **kwargs):
        usages = self.get_object().usage_set.all()
        generics_involved, orphaned_licenses = get_usages_obligations(usages)

        return Response(
            {
                "generics": GenericSerializer(generics_involved, many=True).data,
                "orphaned": LicenseSerializer(orphaned_licenses, many=True).data,
            }
        )


class UploadSPDXViewSet(CreateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows to upload an SPDX file to Hermine.
    """

    serializer_class = UploadSPDXSerializer

    @swagger_auto_schema(responses={201: "Created"})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        spdx_file = serializer.validated_data["spdx_file"]
        release = serializer.validated_data["release"]
        import_spdx_file(
            spdx_file,
            release.pk,
            serializer.validated_data.get("replace", False),
            defaults={"linking": serializer.validated_data.get("linking")},
        )
        return Response()


class UploadORTViewSet(CreateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows to upload an ORT output file to Hermine.
    """

    serializer_class = UploadORTSerializer

    @swagger_auto_schema(responses={201: "Created"})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        ort_file = serializer.validated_data["ort_file"]
        release = serializer.validated_data["release_id"]
        import_ort_evaluated_model_json_file(
            ort_file,
            release.id,
            serializer.validated_date.get("replace", False),
            defaults={"linking": serializer.validated_data.get("linking")},
        )
        return Response()


class ComponentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows components to be viewed or edited
    """

    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    lookup_field = "pk"


class VersionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows versions to be viewed or edited.
    """

    queryset = Version.objects.all()

    def get_queryset(self):
        """
        Handles if the user is accessing the viewset from root of api or from a nested
        componentset in a license


        :return: All the versions if query is made from /api/versions/, or only the
            relevant version if query is made from
            /api/components/<int: componen_id>/versions
        :rtype: QuerySet
        """
        qs = super().get_queryset()

        if component := self.kwargs.get("nested_1_pk") is not None:
            qs = qs.filter(component=component)

        return qs

    def perform_create(self, serializer):
        serializer.save(component_id=self.kwargs.get("nested_1_pk"))

    serializer_class = VersionSerializer
    lookup_field = "id"


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


class LicenseChoiceViewSet(viewsets.ModelViewSet):
    queryset = LicenseChoice.objects.all()
    serializer_class = LicenseChoiceSerializer
