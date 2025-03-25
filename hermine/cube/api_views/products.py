#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from itertools import groupby, chain

from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from junit_xml import TestCase, TestSuite, to_xml_report_string
from rest_framework import serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from cube.importers import (
    add_import_history_entry,
    import_spdx_file,
    import_cyclonedx_file,
    import_ort_evaluated_model_json_file,
    add_dependency,
)
from cube.models import Product, Release, Exploitation
from cube.models import SBOMImport
from cube.permissions import UpdateSBOMPermissions
from cube.serializers import (
    ReleaseSerializer,
    UploadSPDXSerializer,
    UploadCycloneDXSerializer,
    UploadORTSerializer,
    DependencySerializer,
    CompatibilityValidationSerializer,
)
from cube.serializers.components import UsageSerializer
from cube.serializers.products import (
    ProductSerializer,
    ExpressionValidationSerializer,
    AndsValidationSerializer,
    ChoicesValidationSerializer,
    PolicyValidationSerializer,
    ExploitationSerializer,
    ExploitationsValidationSerializer,
    ReleaseObligationsSerializer,
    ReleaseLicensesSerializer,
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
    validate_compatibility,
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name is not None:
            queryset = self.queryset.filter(name=name)
        return queryset


class ReleaseViewSet(viewsets.ModelViewSet):
    serializer_class = ReleaseSerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        Handles if the user is accessing the viewset from root of api or from a
        nested #ReleaseSet in a product (api/products/<int:product_id>/releases)

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
        responses={200: ExpressionValidationSerializer()},
    )
    @action(detail=True, methods=["get"])
    def validation_1(self, request, **kwargs):
        """
        Check for components versions that do not have valid SPDX license
        expressions.
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
        responses={200: AndsValidationSerializer()},
    )
    @action(detail=True, methods=["get"])
    def validation_2(self, request, **kwargs):
        """
        Confirm ANDs operators in SPDX expressions are not poorly registered ORs
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
        responses={200: ExploitationsValidationSerializer()},
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
        responses={200: ChoicesValidationSerializer()},
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
        responses={200: PolicyValidationSerializer()},
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
        responses={200: CompatibilityValidationSerializer()},
    )
    @action(detail=True, methods=["get"])
    def validation_6(self, request, **kwargs):
        """
        Check that the licenses are compatible with policy.
        """
        response = {}
        release = self.get_object()

        response["valid"], context = validate_compatibility(release)
        response.update(context)
        response["details"] = reverse(
            "cube:release_validation", kwargs={"pk": release.pk}
        )

        return Response(CompatibilityValidationSerializer(response).data)

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
    )
    @action(
        detail=True,
        methods=["get"],
    )
    def junit(self, request, **kwargs):
        """
        Returns a JUnit report for the validation steps of the release.
        """
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

    @swagger_auto_schema(
        responses={200: ReleaseObligationsSerializer()},
    )
    @action(detail=True, methods=["get"])
    def obligations(self, pk, **kwargs):
        """
        Returns the obligations (generic and license specific) of the release.
        """
        usages = self.get_object().usage_set.all()
        generics_involved, specifics, licenses_involved = get_usages_obligations(usages)
        response = {
            "generics": generics_involved,
            "obligations": specifics,
            "licenses": licenses_involved,
        }

        return Response(ReleaseObligationsSerializer(response).data)

    @swagger_auto_schema(
        responses={200: ReleaseLicensesSerializer()},
    )
    @action(detail=True, methods=["get"])
    def licenses(self, pk, **kwargs):
        """
        List license involved in the release, grouped by project / scope / exploitation.
        """
        usages = sorted(
            self.get_object().usage_set.all(),
            key=lambda u: (u.project, u.scope, u.exploitation),
        )

        # build the project / scope / exploitations tree
        response = {
            "projects": [
                {
                    "name": project_name,
                    "licenses": set(
                        chain.from_iterable(
                            usage.licenses_chosen.all()
                            for usage in self.get_object()
                            .usage_set.filter(project=project_name)
                            .prefetch_related("licenses_chosen")
                        )
                    ),
                    "scopes": [
                        {
                            "name": scope_name,
                            "licenses": set(
                                chain.from_iterable(
                                    usage.licenses_chosen.all()
                                    for usage in self.get_object()
                                    .usage_set.filter(
                                        project=project_name, scope=scope_name
                                    )
                                    .prefetch_related("licenses_chosen")
                                )
                            ),
                            "exploitations": [
                                {
                                    "name": exploitation_name,
                                    "licenses": set(
                                        chain.from_iterable(
                                            usage.licenses_chosen.all()
                                            for usage in self.get_object()
                                            .usage_set.filter(
                                                project=project_name,
                                                scope=scope_name,
                                                exploitation=exploitation_name,
                                            )
                                            .prefetch_related("licenses_chosen")
                                        )
                                    ),
                                }
                                for exploitation_name, exploitation_usages in groupby(
                                    scope_usages, key=lambda u: u.exploitation
                                )
                            ],
                        }
                        for scope_name, scope_usages in groupby(
                            project_usages, key=lambda u: u.scope
                        )
                    ],
                }
                for project_name, project_usages in groupby(
                    usages, key=lambda u: u.project
                )
            ],
        }

        return Response(ReleaseLicensesSerializer(response).data)


class ExploitationViewSet(viewsets.ModelViewSet):
    serializer_class = ExploitationSerializer
    lookup_field = "id"

    def get_queryset(self):
        if "release_id" not in self.kwargs:
            # Ony used by yasg when it tries to check permissions on the viexw
            return Exploitation.objects.all()
        return Exploitation.objects.filter(release=self.kwargs["release_id"])

    def perform_create(self, serializer):
        serializer.save(release_id=self.kwargs["release_id"])


@method_decorator(
    name="create", decorator=swagger_auto_schema(responses={201: "Created"})
)
class UploadSPDXViewSet(CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [UpdateSBOMPermissions]
    serializer_class = UploadSPDXSerializer
    parser_classes = (MultiPartParser,)

    # Necessary for deprecated endpoints
    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        if "release_id" in self.kwargs:
            del serializer.fields["release"]
        return serializer

    @transaction.atomic()
    def perform_create(self, serializer):
        spdx_file = serializer.validated_data["spdx_file"]
        if "release_id" in self.kwargs:
            release_id = self.kwargs["release_id"]
        else:
            release_id = serializer.validated_data["release"].id
        import_spdx_file(
            spdx_file,
            release_id,
            serializer.validated_data.get("replace", False),
            linking=serializer.validated_data.get("linking", ""),
            default_project_name=serializer.validated_data.get(
                "default_project_name", ""
            ),
            default_scope_name=serializer.validated_data.get("default_scope_name", ""),
        )
        add_import_history_entry(
            spdx_file,
            SBOMImport.BOM_SPDX,
            serializer.validated_data.get("replace", False),
            serializer.validated_data.get("linking", ""),
            self.request.user,
            release_id,
        )
        return Response(status=status.HTTP_201_CREATED)


@method_decorator(
    name="create", decorator=swagger_auto_schema(responses={201: "Created"})
)
class UploadCYCLONEDXViewSet(CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [UpdateSBOMPermissions]
    serializer_class = UploadCycloneDXSerializer
    parser_classes = (MultiPartParser,)

    # Necessary for deprecated endpoints
    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        if "release_id" in self.kwargs:
            del serializer.fields["release"]
        return serializer

    @transaction.atomic()
    def perform_create(self, serializer):
        cyclonedx_file = serializer.validated_data["cyclonedx_file"]
        if "release_id" in self.kwargs:
            release_id = self.kwargs["release_id"]
        else:
            release_id = serializer.validated_data["release"].id
        import_cyclonedx_file(
            cyclonedx_file,
            release_id,
            serializer.validated_data.get("replace", False),
            linking=serializer.validated_data.get("linking", ""),
            default_project_name=serializer.validated_data.get(
                "default_project_name", ""
            ),
            default_scope_name=serializer.validated_data.get("default_scope_name", ""),
        )
        add_import_history_entry(
            cyclonedx_file,
            SBOMImport.BOM_CYCLONEDX,
            serializer.validated_data.get("replace", False),
            serializer.validated_data.get("linking", ""),
            self.request.user,
            release_id,
        )
        return Response(status=status.HTTP_201_CREATED)


@method_decorator(
    name="create", decorator=swagger_auto_schema(responses={201: "Created"})
)
class UploadORTViewSet(CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [UpdateSBOMPermissions]
    serializer_class = UploadORTSerializer
    parser_classes = (MultiPartParser,)

    # Necessary for deprecated endpoints
    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        if "release_id" in self.kwargs:
            del serializer.fields["release"]
        return serializer

    @transaction.atomic()
    def perform_create(self, serializer):
        ort_file = serializer.validated_data["ort_file"]
        if "release_id" in self.kwargs:
            release_id = self.kwargs["release_id"]
        else:
            release_id = serializer.validated_data["release"].id
        import_ort_evaluated_model_json_file(
            ort_file,
            release_id,
            serializer.validated_data.get("replace", False),
            linking=serializer.validated_data.get("linking", ""),
        )
        add_import_history_entry(
            ort_file,
            SBOMImport.BOM_ORT,
            serializer.validated_data.get("replace", False),
            serializer.validated_data.get("linking", ""),
            self.request.user,
            release_id,
        )
        return Response(status=status.HTTP_201_CREATED)


@method_decorator(
    name="create", decorator=swagger_auto_schema(responses={201: UsageSerializer()})
)
class CreateSingleDependencyViewSet(CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [UpdateSBOMPermissions]
    serializer_class = DependencySerializer

    # Necessary for deprecated endpoints
    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        if "release_id" in self.kwargs:
            del serializer.fields["release"]
        return serializer

    def perform_create(self, serializer):
        if "release_id" in self.kwargs:
            release_id = self.kwargs["release_id"]
        else:
            release_id = serializer.validated_data["release"].id
        purl_type = serializer.validated_data["purl_type"]
        name = serializer.validated_data["name"]
        try:
            usage, _ = add_dependency(
                release_id,
                purl_type,
                name,
                version_number=serializer.validated_data.get(
                    "version_number", "Current"
                ),
                concluded_license=serializer.validated_data.get(
                    "spdx_valid_license_expr", ""
                ),
                declared_license=serializer.validated_data.get(
                    "declared_license_expr", ""
                ),
                purl=serializer.validated_data.get("purl", ""),
                scope=serializer.validated_data.get("default_scope_name", ""),
                linking=serializer.validated_data.get("linking", ""),
                project=serializer.validated_data.get("default_project_name", ""),
                component_defaults={
                    "homepage_url": serializer.validated_data.get("homepage_url", ""),
                    "description": serializer.validated_data.get("description", ""),
                },
            )
            return Response(UsageSerializer(usage).data)
        except ValueError as e:
            raise serializers.ValidationError(e)
