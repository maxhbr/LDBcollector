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
    GenericSerializer,
)
from cube.serializers import (
    ReleaseSerializer,
    LicenseSerializer,
    UploadSPDXSerializer,
    UploadORTSerializer,
)
from cube.serializers.products import (
    ProductSerializer,
    ExpressionValidationSerializer,
    AndsValidationSerializer,
    ChoicesValidationSerializer,
    PolicyValidationSerializer,
    ExploitationSerializer,
    ExploitationsValidationSerializer,
)
from cube.utils.licenses import get_usages_obligations
from cube.utils.release_validation import (
    update_validation_step,
    validate_expressions,
    validate_ands,
    validate_exploitations,
    validate_choices,
    validate_policy,
    apply_curations,
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
        responses={200: ExpressionValidationSerializer},
    )
    @action(detail=True, methods=["get"])
    def validation_1(self, request, **kwargs):
        """
        Check for components versions that do not have valid SPDX license expressions.
        """
        response = {}
        release = self.get_object()
        apply_curations(release)

        response["valid"], context = validate_expressions(release)
        response["invalid_expressions"] = [
            usage.version for usage in context["invalid_expressions"]
        ]
        response["fixed_expressions"] = [
            usage.version for usage in context["fixed_expressions"]
        ]
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

        return Response(ExpressionValidationSerializer(response).data)

    @swagger_auto_schema(
        responses={200: AndsValidationSerializer},
    )
    @action(detail=True, methods=["get"])
    def validation_2(self, request, **kwargs):
        """
        Confirm ANDs operators in SPDX expressions are not poorly registered ORs.
        """
        response = {}
        release = self.get_object()
        apply_curations(release)

        response["valid"], context = validate_ands(release)
        response["to_confirm"] = context["to_confirm"]
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

        return Response(AndsValidationSerializer(response).data)

    @swagger_auto_schema(
        responses={200: ExploitationsValidationSerializer},
    )
    @action(detail=True, methods=["get"])
    def validation_3(self, request, **kwargs):
        """
        Check all scopes have a defined exploitation
        """
        response = {}
        release = self.get_object()

        response["valid"], context = validate_exploitations(release)
        response["exploitations"] = context["exploitations"]
        response["unset_scopes"] = context["unset_scopes"]
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

        return Response(ExploitationsValidationSerializer(response).data)

    @swagger_auto_schema(
        responses={200: ChoicesValidationSerializer},
    )
    @action(detail=True, methods=["get"])
    def validation_4(self, request, **kwargs):
        """
        Check all licenses choices are done.
        """
        response = {}
        release = self.get_object()

        response["valid"], context = validate_choices(release)
        response.update(context)
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

        return Response(ChoicesValidationSerializer(response).data)

    @swagger_auto_schema(
        responses={200: PolicyValidationSerializer},
    )
    @action(detail=True, methods=["get"])
    def validation_5(self, request, **kwargs):
        """
        Check that the licenses are compatible with policy.
        """
        response = {}
        release = self.get_object()

        response["valid"], context = validate_policy(release)
        response.update(context)
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

        return Response(PolicyValidationSerializer(response).data)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "An XML Junit report",
                examples={
                    "text/xml": """
<?xml version="1.0" ?>
<testsuites disabled="0" errors="0" failures="1" tests="4">
    <testsuite disabled="0" errors="0" failures="1" name="Foobar" skipped="0" tests="4" time="0">
        <testcase name="Licenses curation"/>
        <testcase name="ANDs confirmation"/>
        <testcase name="Scope exploitations"/>
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
        apply_curations(release)

        expressions_step = TestCase(
            "Licenses curation",
        )
        valid, context = validate_expressions(release)
        if not valid:
            expressions_step.add_failure_info(
                message=f"{len(context['invalid_expressions'])} components license information are not valid SPDX expressions"
            )

        ands_step = TestCase("ANDs confirmation")
        valid, context = validate_ands(release)
        if not valid:
            ands_step.add_failure_info(
                f"{len(context['to_confirm'])} expressions are ambiguous"
            )

        exploitation_step = TestCase("Scope exploitations")
        valid, context = validate_exploitations(release)
        if not valid:
            exploitation_step.add_failure_info(
                f"{len(context['unset_scopes'])} scopes have no exploitation defined"
            )

        choices_step = TestCase("License choices")
        valid, context = validate_choices(release)
        if not valid:
            choices_step.add_failure_info(
                f"{len(context['to_resolve'])} licenses choices to resolve"
            )

        policy_step = TestCase("Policy compatibility")
        valid, context = validate_policy(release)
        if not valid:
            count = (
                len(context["usages_lic_never_allowed"])
                + len(context["usages_lic_context_allowed"])
                + len(context["usages_lic_unknown"])
            )
            policy_step.add_failure_info(f"{count} invalid component usages")

        ts = TestSuite(
            f"{release} Hermine validation steps",
            [expressions_step, ands_step, exploitation_step, choices_step, policy_step],
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
