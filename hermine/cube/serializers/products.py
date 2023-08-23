#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import serializers

from cube.models import Product, Release, Usage, Exploitation
from cube.serializers import (
    UsageSerializer,
    LicenseSerializer,
    VersionSerializer,
    DerogationSerializer,
    GenericSerializer,
    ObligationSerializer,
)


class ExploitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exploitation
        fields = ["scope", "project", "exploitation"]


class ReleaseSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Releases on the following fields :"""

    validation_step = serializers.IntegerField(source="valid_step", read_only=True)
    exploitations = ExploitationSerializer(many=True, read_only=True)

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
        read_only=False, many=True, allow_null=True, required=False
    )

    class Meta:
        use_natural_foreign_keys = True
        model = Product
        fields = ["id", "name", "description", "owner", "releases"]
        read_only_field = "name"

    def create(self, validated_data):
        releases_data = validated_data.pop("releases", [])
        product = Product.objects.create(**validated_data)
        for release_data in releases_data:
            try:
                Release.objects.create(product=product, **release_data)
            except Exception:
                print("Could not create release ", release_data, " of ", product)
        return product

    def update(self, instance, validated_data):
        """Updates a product overwriting existing data. You should explicitely give
        every data you want to keep in the 'validated data parameter.

        :param instance: The instance of product you want to update.
        :type instance: Product
        :param validated_data: A dict matching product serialization. Releases are
            nested in 'releases'.
        :type validated_data: [type]
        :return: [description]
        :rtype: [type]
        """

        Release.objects.filter(product=instance).delete()
        releases_data = validated_data.pop("releases")
        for release_data in releases_data:
            updated_release = Release.objects.create(**release_data, product=instance)
            try:
                instance.releases.add(updated_release)
            except Exception:
                print("Could not create releases of", instance)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


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


class UploadSPDXSerializer(serializers.Serializer):
    spdx_file = serializers.FileField()
    release = serializers.PrimaryKeyRelatedField(queryset=Release.objects.all())
    replace = serializers.BooleanField(default=False, required=False)
    linking = serializers.ChoiceField(choices=Usage.LINKING_CHOICES, required=False)


class UploadORTSerializer(serializers.Serializer):
    ort_file = serializers.FileField()
    release = serializers.PrimaryKeyRelatedField(queryset=Release.objects.all())
    replace = serializers.BooleanField(default=False, required=False)
    linking = serializers.ChoiceField(choices=Usage.LINKING_CHOICES, required=False)
