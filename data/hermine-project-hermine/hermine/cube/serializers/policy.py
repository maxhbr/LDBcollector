#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import serializers

from cube.models import LicenseChoice, Derogation, LicenseCuration


class LicenseCurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseCuration
        fields = "__all__"


class LicenseChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseChoice
        fields = "__all__"


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
