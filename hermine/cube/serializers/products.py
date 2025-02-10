#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import serializers

from cube.models import Product, Release, Usage, Exploitation, License
from cube.serializers import (
    UsageSerializer,
    LicenseSerializer,
    VersionSerializer,
    DerogationSerializer,
    GenericSerializer,
    ObligationSerializer,
)
from cube.utils.validators import validate_file_size


class ExploitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exploitation
        fields = ["id", "scope", "project", "exploitation"]


class ReleaseSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Releases on the following fields :"""

    validation_step = serializers.IntegerField(source="valid_step", read_only=True)
    exploitations = ExploitationSerializer(many=True, read_only=True)
    outbound_licenses = serializers.SlugRelatedField(
        many=True, slug_field="spdx_id", queryset=License.objects.all(), required=False
    )

    class Meta:
        use_natural_foreign_keys = True
        model = Release
        fields = [
            "id",
            "product",
            "release_number",
            "ship_status",
            "pub_date",
            "validation_step",
            "commit",
            "exploitations",
            "outbound_licenses",
        ]


class ReleaseObligationsSerializer(serializers.Serializer):
    generics = GenericSerializer(many=True, read_only=True)
    obligations = ObligationSerializer(many=True, read_only=True)
    licenses = LicenseSerializer(many=True, read_only=True)


class ReleaseLicensesSerializer(serializers.Serializer):
    class ReleaseLicensesProjectSerializer(serializers.Serializer):
        class ReleaseLicensesScopeSerializer(serializers.Serializer):
            class ReleaseLicensesExploitationSerializer(serializers.Serializer):
                name = serializers.CharField()
                licenses = serializers.StringRelatedField(many=True, read_only=True)

            name = serializers.CharField()
            licenses = serializers.StringRelatedField(many=True, read_only=True)
            exploitations = ReleaseLicensesExploitationSerializer(
                many=True, read_only=True
            )

        name = serializers.CharField()
        licenses = serializers.StringRelatedField(many=True, read_only=True)
        scopes = ReleaseLicensesScopeSerializer(many=True, read_only=True)

    licenses = serializers.StringRelatedField(many=True, read_only=True)
    projects = ReleaseLicensesProjectSerializer(many=True, read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Products on the following fields :"""

    releases = ReleaseSerializer(
        read_only=True, many=True, allow_null=True, required=False
    )
    outbound_licenses = serializers.SlugRelatedField(
        many=True, slug_field="spdx_id", queryset=License.objects.all(), required=False
    )

    class Meta:
        use_natural_foreign_keys = True
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "releases",
            "outbound_licenses",
        ]
        read_only_field = "name"


## Validation step serializers


class BaseValidationStepSerializer(serializers.Serializer):
    valid = serializers.BooleanField(label="Step is valid", read_only=True)
    details = serializers.URLField(read_only=True)


class ExpressionValidationSerializer(BaseValidationStepSerializer):
    invalid_expressions = VersionSerializer(read_only=True, many=True)
    fixed_expressions = VersionSerializer(read_only=True, many=True)


class AndsValidationSerializer(BaseValidationStepSerializer):
    to_confirm = UsageSerializer(read_only=True, many=True)


class ExploitationsValidationSerializer(BaseValidationStepSerializer):
    exploitations = ExploitationSerializer(read_only=True, many=True)
    unset_scopes = serializers.ListSerializer(
        child=serializers.CharField(), read_only=True
    )


class ChoicesValidationSerializer(BaseValidationStepSerializer):
    to_resolve = UsageSerializer(read_only=True, many=True)
    resolved = UsageSerializer(read_only=True, many=True)


class PolicyValidationSerializer(BaseValidationStepSerializer):
    usages_lic_never_allowed = UsageSerializer(read_only=True, many=True)
    usages_lic_context_allowed = UsageSerializer(read_only=True, many=True)
    usages_lic_unknown = UsageSerializer(read_only=True, many=True)
    involved_lic = LicenseSerializer(read_only=True, many=True)
    derogations = DerogationSerializer(read_only=True, many=True)


class CompatibilityValidationSerializer(BaseValidationStepSerializer):
    incompatible_usages = UsageSerializer(read_only=True, many=True)
    incompatible_licenses = LicenseSerializer(read_only=True, many=True)


class UploadSPDXSerializer(serializers.Serializer):
    spdx_file = serializers.FileField(validators=[validate_file_size])
    release = serializers.PrimaryKeyRelatedField(queryset=Release.objects.all())
    replace = serializers.BooleanField(default=False, required=False)
    linking = serializers.ChoiceField(choices=Usage.LINKING_CHOICES, required=False)
    default_project_name = serializers.CharField(
        max_length=Usage.MAX_LENGTH_DEFAULT_PROJECT_NAME, required=False
    )
    default_scope_name = serializers.CharField(
        max_length=Usage.MAX_LENGTH_DEFAULT_SCOPE_NAME, required=False
    )


class UploadCycloneDXSerializer(serializers.Serializer):
    cyclonedx_file = serializers.FileField(validators=[validate_file_size])
    release = serializers.PrimaryKeyRelatedField(queryset=Release.objects.all())
    replace = serializers.BooleanField(default=False, required=False)
    linking = serializers.ChoiceField(choices=Usage.LINKING_CHOICES, required=False)
    default_project_name = serializers.CharField(max_length=750, required=False)
    default_scope_name = serializers.CharField(max_length=50, required=False)


class UploadORTSerializer(serializers.Serializer):
    ort_file = serializers.FileField(validators=[validate_file_size])
    release = serializers.PrimaryKeyRelatedField(queryset=Release.objects.all())
    replace = serializers.BooleanField(default=False, required=False)
    linking = serializers.ChoiceField(choices=Usage.LINKING_CHOICES, required=False)


class DependencySerializer(serializers.Serializer):
    release = serializers.PrimaryKeyRelatedField(queryset=Release.objects.all())
    purl_type = serializers.CharField(max_length=200, required=True)
    name = serializers.CharField(max_length=200, required=True)
    version_number = serializers.CharField(max_length=200, required=True)
    declared_license_expr = serializers.CharField(max_length=500, required=False)
    spdx_valid_license_expr = serializers.CharField(max_length=500, required=False)
    linking = serializers.ChoiceField(choices=Usage.LINKING_CHOICES, required=False)
    purl = serializers.CharField(max_length=250, required=False)
    default_project_name = serializers.CharField(max_length=750, required=False)
    default_scope_name = serializers.CharField(max_length=50, required=False)
    homepage_url = serializers.CharField(max_length=500, required=False)
    description = serializers.CharField(max_length=500, required=False)
