#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import viewsets

from cube.models import LicenseChoice
from cube.serializers import (
    LicenseChoiceSerializer,
)


class LicenseChoiceViewSet(viewsets.ModelViewSet):
    queryset = LicenseChoice.objects.all()
    serializer_class = LicenseChoiceSerializer
