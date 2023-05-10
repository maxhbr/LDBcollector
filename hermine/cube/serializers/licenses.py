#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import serializers

from cube.models import License, Obligation, Generic, Team


class GenericNameField(serializers.CharField):
    """A class that allows us to add an extra field "generic_name" in serialization of
    Obligation."""

    def get_attribute(self, instance):
        return instance.generic.name if instance.generic is not None else None


class ObligationSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of obligations on the following fields :
    "name", "license", "verbatim", "passivity", "trigger_expl", "trigger_mdf",
    "generic_id"

    :param serializers:
        https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    generic_name = GenericNameField(allow_null=True, required=False)

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
            "generic",
            "generic_name",
        ]

    def get_generic_name(self, instance):
        generic = instance.generic
        return generic.name if generic is not None else None

    @classmethod
    def create(cls, validated_data):
        # When creating new obligation, we link it to a generic obligation if one with
        # the same **name** exists in base.
        generic_name = validated_data.pop("generic_name", None)
        if generic_name is not None:
            validated_data["generic"] = Generic.objects.get(name=generic_name)
        instance = Obligation.objects.create(**validated_data)
        return instance

    @classmethod
    def update(cls, instance, validated_data):
        generic_name = validated_data.pop("generic_name", None)
        if generic_name is not None:
            validated_data["generic"] = Generic.objects.get(name=generic_name)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class LicenseObligationSerializer(ObligationSerializer):
    """A serializer used for nested representation of Obligations. We don't need and
    we cannot fill the license field in that case.

    :param ObligationSerializer: The main serializer for obligations
    :type ObligationSerializer: Serializer
    """

    class Meta:
        model = Obligation
        exclude = ["license"]

    @classmethod
    def create(cls, license, validated_data):
        validated_data["license"] = license
        instance = Obligation.objects.create(**validated_data)
        return instance

    @classmethod
    def update(cls, instance, license, validated_data):
        validated_data["license"] = license
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class LicenseSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of licenses on the following fields:
    "spdx_id", "long_name", "license_version", "radical", "autoupgrade", "steward",
    "inspiration_spdx", "copyleft", "color", "color_explanation", "url", "osi_approved",
    "fsf_approved", "foss", "patent_grant", "ethical_clause", "non_commercial",
    "non_tivoisation", "jurisdictional_clause","comment", "verbatim","obligation_set"

    Obligations are nested in a license, and can be accessed with
    "/licenses/{license_name}/obligation/{obligation_name}"

    :param serializers:
        https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    obligation_set = LicenseObligationSerializer(
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
            "allowed",
            "allowed_explanation",
            "url",
            "osi_approved",
            "fsf_approved",
            "foss",
            "patent_grant",
            "ethical_clause",
            "non_commercial",
            "non_tivoisation",
            "law_choice",
            "venue_choice",
            "liability",
            "warranty",
            "comment",
            "verbatim",
            "obligation_set",
        ]
        read_only_field = "spdx_id"

    def create(self, validated_data):
        obligations_data = validated_data.pop("obligation_set")
        license = License.objects.create(**validated_data)
        for obligation_data in obligations_data:
            LicenseObligationSerializer.create(license.id, obligation_data)
        return license

    def update(self, instance, validated_data):
        """Updates a license overwriting existing data. You should explicitely give
        every data you want to keep in the 'validated data parameter.

        :param instance: The instance of license you want to update.
        :type instance: License
        :param validated_data: A dict matching license serialization.
            Obligations are nested in 'obligation_set'.
        :type validated_data: [type]
        :return: [description]
        :rtype: [type]
        """

        Obligation.objects.filter(license=instance).delete()
        obligations_data = validated_data.pop("obligation_set")
        for obligation_data in obligations_data:
            LicenseObligationSerializer.create(instance, obligation_data)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class GenericSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of generic obligations on the following
    fields:
    "id", "name", "description", "in_core", "metacategory", "team", "passivity"
    Here the id is kept because generic obligations are considered as something so
    important to the work of Hermine that keeping a surrogate key to point them is
    reasonable.

    :param serializers:
        https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    triggered_by = serializers.ListField(
        read_only=True, child=serializers.CharField(read_only=True)
    )
    team = serializers.SlugRelatedField(
        slug_field="name", queryset=Team.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Generic
        fields = [
            "id",
            "name",
            "description",
            "in_core",
            "metacategory",
            "team",
            "passivity",
            "triggered_by",
        ]
