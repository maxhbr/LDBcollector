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
)


class ExploitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exploitation
        fields = ["scope", "project", "exploitation"]


class ReleaseSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Releases on the following fields :


    :param serializers:
        https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

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


class ProductSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Products on the following fields :

    :param serializers:
        https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

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
                instance.obligation_set.add(updated_release)
            except Exception:
                print("Could not create releases of", instance)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class Validation1Serializer(serializers.Serializer):
    valid = serializers.BooleanField(label="Step is valid", read_only=True)
    invalid_expressions = VersionSerializer(read_only=True, many=True)
    fixed_expressions = VersionSerializer(read_only=True, many=True)
    details = serializers.URLField(read_only=True)


class Validation2Serializer(serializers.Serializer):
    valid = serializers.BooleanField(label="Step is valid", read_only=True)
    licenses_to_check = LicenseSerializer(read_only=True, many=True)
    licenses_to_create = serializers.ListField(
        read_only=True, child=serializers.CharField()
    )
    details = serializers.URLField(read_only=True)


class Validation3Serializer(serializers.Serializer):
    valid = serializers.BooleanField(label="Step is valid", read_only=True)
    to_confirm = VersionSerializer(read_only=True, many=True)
    details = serializers.URLField(read_only=True)


class Validation4Serializer(serializers.Serializer):
    valid = serializers.BooleanField(label="Step is valid", read_only=True)
    to_resolve = UsageSerializer(read_only=True, many=True)
    resolved = UsageSerializer(read_only=True, many=True)
    details = serializers.URLField(read_only=True)


class Validation5Serializer(serializers.Serializer):
    valid = serializers.BooleanField(label="Step is valid", read_only=True)
    usages_lic_never_allowed = UsageSerializer(read_only=True, many=True)
    usages_lic_context_allowed = UsageSerializer(read_only=True, many=True)
    usages_lic_unknown = UsageSerializer(read_only=True, many=True)
    involved_lic = LicenseSerializer(read_only=True, many=True)
    derogations = DerogationSerializer(read_only=True, many=True)
    details = serializers.URLField(read_only=True)


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
