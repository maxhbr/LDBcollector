# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import serializers
from cube.models import (
    License,
    Obligation,
    Generic,
    Usage,
    Release,
    Product,
    Component,
    Version,
    Derogation,
)

"""
Serializers allow complex data such as querysets and model instances to be converted to native Python datatypes that can then be easily rendered into JSON, XML or other content types. Serializers also provide deserialization, allowing parsed data to be converted back into complex types, after first validating the incoming data. Here the serialization is based on the Django REST Framework (DRF).
"""


class ObligationSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of obligations on the following fields :
    "name", "license", "verbatim", "passivity", "trigger_expl", "trigger_mdf", "generic_id"

    :param serializers: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    class Meta:
        use_natural_foreign_keys = True
        model = Obligation
        fields = [
            "id",
            "license",
            "name",
            "verbatim",
            "passivity",
            "trigger_expl",
            "trigger_mdf",
            "generic_id",
        ]


class LicenseSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of licenses on the following fields :
    "spdx_id", "long_name", "license_version", "radical", "autoupgrade", "steward", "inspiration_spdx", "copyleft", "color", "color_explanation", "url", "osi_approved", "fsf_approved", "foss", "patent_grant", "ethical_clause", "non_commmercial", "legal_uncertainty", "non_tivoisation", "technical_nature_constraint", "jurisdictional_clause","comment", "verbatim","obligation_set"
    Obligations are nested in a license, and can be accessed with "/licenses/{license_name}/obligation/{obligation_name}"

    :param serializers: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    obligation_set = ObligationSerializer(
        read_only=False, many=True, allow_null=True, required=False
    )

    class Meta:
        use_natural_foreign_keys = True
        model = License
        fields = [
            "id",
            "spdx_id",
            "long_name",
            "license_version",
            "radical",
            "autoupgrade",
            "steward",
            "inspiration_spdx",
            "copyleft",
            "color",
            "color_explanation",
            "url",
            "osi_approved",
            "fsf_approved",
            "foss",
            "patent_grant",
            "ethical_clause",
            "non_commmercial",
            "legal_uncertainty",
            "non_tivoisation",
            "technical_nature_constraint",
            "law_choice",
            "comment",
            "verbatim",
            "obligation_set",
        ]
        read_only_field = "spdx_id"

    def create(self, validated_data):
        obligations_data = validated_data.pop("obligation_set")
        license = License.objects.create(**validated_data)
        for obligation_data in obligations_data:
            try:
                Obligation.objects.create(license=license, **obligation_data)
            except Exception:
                print("Could not create obligations of", license)
        return license

    def update(self, instance, validated_data):
        """Updates a license overwriting existing data. You should explicitely give every data you want to keep in the 'validated data parameter.

        :param instance: The instance of license you want to update.
        :type instance: License
        :param validated_data: A dict matching license serialization. Obligations are nested in 'obligation_set'.
        :type validated_data: [type]
        :return: [description]
        :rtype: [type]
        """

        Obligation.objects.filter(license=instance).delete()
        obligations_data = validated_data.pop("obligation_set")
        for obligation_data in obligations_data:
            if obligation_data["generic_id"]:
                obligation_data["generic_id"] = obligation_data["generic_id"].id
            updated_obligation = Obligation.objects.create(
                **obligation_data, license=instance
            )
            try:
                instance.obligation_set.add(updated_obligation)
            except Exception:
                print("Could not create obligations of", instance)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class GenericSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of generic obligations on the following fields :
    "id", "name", "description", "in_core", "metacategory", "team", "passivity"
    Here the id is kept because generic obligations are considered as something so important to the work of Hermine that keeping a surrogate key to point them is reasonable.

    :param serializers: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    class Meta:
        use_natural_foreign_keys = True
        model = Generic
        fields = [
            "id",
            "name",
            "description",
            "in_core",
            "metacategory",
            "team",
            "passivity",
        ]


class UsageSerializer(serializers.ModelSerializer):
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
            "scope",
        ]


class ExploitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usage
        use_natural_foreign_keys = True
        release_id = serializers.PrimaryKeyRelatedField(
            many=False, read_only=True, allow_null=True
        )
        fields = ["id", "release", "version", "exploitation", "scope"]


class ReleaseSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Releases on the following fields :


    :param serializers: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    class Meta:
        use_natural_foreign_keys = True
        model = Release
        fields = [
            "id",
            "product",
            "release_number",
            "ship_status",
            "pub_date",
            "valid_step",
        ]


class ProductSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Products on the following fields :

    :param serializers: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    release_set = ReleaseSerializer(
        read_only=False, many=True, allow_null=True, required=False
    )

    class Meta:
        use_natural_foreign_keys = True
        model = Product
        fields = ["id", "name", "description", "owner", "release_set"]
        read_only_field = "name"

    def create(self, validated_data):
        releases_data = validated_data.pop("release_set")
        product = Product.objects.create(**validated_data)
        for release_data in releases_data:
            try:
                Release.objects.create(product=product, **release_data)
            except Exception:
                print("Could not create release ", release_data, " of ", product)
        return product

    def update(self, instance, validated_data):
        """Updates a product overwriting existing data. You should explicitely give every data you want to keep in the 'validated data parameter.

        :param instance: The instance of product you want to update.
        :type instance: Product
        :param validated_data: A dict matching product serialization. Releases are nested in 'release_set'.
        :type validated_data: [type]
        :return: [description]
        :rtype: [type]
        """

        Release.objects.filter(product=instance).delete()
        releases_data = validated_data.pop("release_set")
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


class VersionSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Versions on the following fields :
    "component", "version_number", "declared_license_expr", "spdx_valid_license_expr", "corrected_license", "scanned_licenses", "purl", 

    :param serializers: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

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
    "id", "name", "package_repo", "description", "programming_language", "spdx_expression", "homepage_url", "export_control_status"

    :param serializers: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    version_set = VersionSerializer(
        read_only=False, many=True, allow_null=True, required=False
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
            "version_set",
        ]
        read_only_field = "name"

    def create(self, validated_data):
        versions_data = validated_data.pop("version_set")
        component = Component.objects.create(**validated_data)
        for version_data in versions_data:
            try:
                Version.objects.create(component=component, **version_data)
            except Exception:
                print("Could not create version ", version_data, " of ", component)
        return component

    def update(self, instance, validated_data):
        """Updates a product overwriting existing data. You should explicitely give every data you want to keep in the 'validated data parameter.

        :param instance: The instance of component you want to update.
        :type instance: Component
        :param validated_data: A dict matching component serialization. Versions are nested in 'version_set'.
        :type validated_data: [type]
        :return: [description]
        :rtype: [type]
        """

        Version.objects.filter(component=instance).delete()
        versions_data = validated_data.pop("version_set")
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


class UploadSPDXSerializer(serializers.Serializer):
    spdx_file = serializers.FileField()
    release_id = serializers.IntegerField()

    class Meta:
        fields = ["release_id", "spdx_file"]


class NormalisedLicensesSerializer(serializers.Serializer):
    unnormalised_license_set = LicenseSerializer(
        read_only=True, many=True, allow_null=True, required=False
    )

    class Meta:
        fields = ["unnormalised_license_set"]


class DerogationSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Derogations on the following fields :
    "license", "release", "usage", "linking", "scope", "justification",
    :param serializers: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    class Meta:
        use_natural_foreign_keys = True
        model = Derogation
        fields = ["license", "release", "usage", "linking", "scope", "justification"]
