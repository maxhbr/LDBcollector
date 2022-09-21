#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.http import HttpResponse
from django.urls import reverse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from junit_xml import TestCase, TestSuite, to_xml_report_string
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from cube.importers import import_spdx_file, import_ort_evaluated_model_json_file
from cube.models import Product, Release, Exploitation
from cube.serializers import (
    ReleaseSerializer,
    LicenseSerializer,
    UploadSPDXSerializer,
    UploadORTSerializer,
)
from cube.serializers.products import (
    ProductSerializer,
    Validation1Serializer,
    Validation2Serializer,
    Validation3Serializer,
    Validation4Serializer,
    Validation5Serializer,
    ExploitationSerializer,
)
from cube.serializers import (
    GenericSerializer,
)
from cube.utils.licenses import get_usages_obligations
from cube.utils.releases import (
    update_validation_step,
    validate_step_1,
    validate_step_2,
    validate_step_3,
    validate_step_4,
    validate_step_5,
)


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
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

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
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

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
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

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
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

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
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

        return Response(Validation5Serializer(response).data)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "An XML Junit report",
                examples={
                    "text/xml": """
<?xml version="1.0" ?>
<testsuites disabled="0" errors="0" failures="1" tests="4">
    <testsuite disabled="0" errors="0" failures="1" name="Foobar" skipped="0" tests="4" time="0">
        <testcase name="Usage normalization"/>
        <testcase name="Licenses"/>
        <testcase name="License choices"/>
        <testcase name="Policy compatibility">
            <failure type="failure" message="3 invalid component usages"/>
        </testcase>
    </testsuite>
</testsuites>
            """
                },
            )
        },
        operation_description="Returns an XML JUnit report, with one testsuite in which is validation step is a testcase.",
    )
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
                len(context["usages_lic_never_allowed"])
                + len(context["usages_lic_context_allowed"])
                + len(context["usages_lic_unknown"])
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


class ExploitationViewSet(viewsets.ModelViewSet):
    serializer_class = ExploitationSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Exploitation.objects.filter(release=self.kwargs["release_id"])

    def perform_create(self, serializer):
        serializer.save(release_id=self.kwargs["release_id"])


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
            linking=serializer.validated_data.get("linking", ""),
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
            linking=serializer.validated_data.get("linking", ""),
        )
        return Response()
