#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import serializers

from cube.models import LicenseChoice, Derogation, LicenseCuration, ExpressionValidation


class LicenseCurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseCuration
        exclude = ("decision_type", "release", "product", "scope")


class ExpressionValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpressionValidation
        exclude = ("decision_type", "release", "product", "scope")


class LicenseChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseChoice
        exclude = ("decision_type",)


class DerogationSerializer(serializers.ModelSerializer):
    """Allow serialization and deserialization of Derogations on the following fields :
    "license", "release", "usage", "linking", "scope", "justification"

    :param serializers:
        https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """

    class Meta:
        use_natural_foreign_keys = True
        model = Derogation
        fields = "__all__"
