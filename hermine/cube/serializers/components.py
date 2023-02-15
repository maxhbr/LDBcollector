#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import serializers

from cube.models import Usage, Version, Component, License
from cube.serializers.policy import LicenseChoiceSerializer


class UsageFlatSerializer(serializers.ModelSerializer):
    """Serializes a usages including the Purl of the Component version
    it uses
    """

    version_purl = serializers.SerializerMethodField()

    class Meta:
        model = Usage
        fields = "__all__"

    def get_version_purl(self, obj):
        return obj.version.purl


class UsageSerializer(serializers.ModelSerializer):
    license_choices = LicenseChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Usage
        use_natural_foreign_keys = True
        release_id = serializers.PrimaryKeyRelatedField(
            many=False, read_only=True, allow_null=True
        )
        fields = [
            "id",
            "release",
            "version",
            "status",
            "addition_method",
            "addition_date",
            "linking",
            "component_modified",
            "exploitation",
            "description",
            "licenses_chosen",
            "license_choices",
            "scope",
            "project",
        ]


class VersionSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Versions on the following fields :
    "component", "version_number", "declared_license_expr", "spdx_valid_license_expr",
    "corrected_license", "scanned_licenses", "purl",

    :param serializers:
        https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    component = serializers.PrimaryKeyRelatedField(read_only=True, required=False)

    class Meta:
        use_natural_foreign_keys = True
        model = Version
        fields = [
            "id",
            "component",
            "version_number",
            "declared_license_expr",
            "spdx_valid_license_expr",
            "corrected_license",
            "purl",
        ]


class ComponentSerializer(serializers.ModelSerializer):
    """
    Allows serialization and deserialization of Products on the following fields :
    "id", "name", "package_repo", "description", "programming_language",
    "spdx_expression", "homepage_url", "export_control_status"

    :param serializers:
        https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    versions = VersionSerializer(
        read_only=False,
        many=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        use_natural_foreign_keys = True
        model = Component
        fields = [
            "id",
            "name",
            "package_repo",
            "description",
            "programming_language",
            "spdx_expression",
            "homepage_url",
            "export_control_status",
            "versions",
        ]
        read_only_field = "name"

    def create(self, validated_data):
        versions_data = validated_data.pop("versions", [])
        component = Component.objects.create(**validated_data)
        for version_data in versions_data:
            try:
                Version.objects.create(component=component, **version_data)
            except Exception:
                print("Could not create version ", version_data, " of ", component)
        return component

    def update(self, instance, validated_data):
        """Updates a product overwriting existing data. You should explicitely give
        every data you want to keep in the 'validated data parameter.

        :param instance: The instance of component you want to update.
        :type instance: Component
        :param validated_data: A dict matching component serialization.
            Versions are nested in 'versions'.
        :type validated_data: [type]
        :return: [description]
        :rtype: [type]
        """

        Version.objects.filter(component=instance).delete()
        versions_data = validated_data.pop("versions", [])
        for version_data in versions_data:
            updated_version = Version.objects.create(**version_data, product=instance)
            try:
                instance.obligation_set.add(updated_version)
            except Exception:
                print("Could not create versions of", instance)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class SBOMItemSerializer(serializers.Serializer):
    package_id = serializers.CharField()
    spdx = serializers.SlugRelatedField(
        queryset=License.objects.all(), slug_field="spdx_id"
    )
    exploitation = serializers.ChoiceField(
        label="Exploitation", choices=Usage.EXPLOITATION_CHOICES
    )
    modification = serializers.ChoiceField(
        label="Modification", choices=Usage.MODIFICATION_CHOICES
    )


class SBOMSerializer(serializers.Serializer):
    packages = SBOMItemSerializer(many=True)
