#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import viewsets

from cube.models import LicenseChoice, LicenseCuration, Derogation
from cube.serializers import (
    LicenseChoiceSerializer,
    LicenseCurationSerializer,
    DerogationSerializer,
)


class SaveAuthorMixin:
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LicenseCurationViewSet(SaveAuthorMixin, viewsets.ModelViewSet):
    queryset = LicenseCuration.objects.all()
    serializer_class = LicenseCurationSerializer


class LicenseChoiceViewSet(SaveAuthorMixin, viewsets.ModelViewSet):
    queryset = LicenseChoice.objects.all()
    serializer_class = LicenseChoiceSerializer


class DerogationViewSet(SaveAuthorMixin, viewsets.ModelViewSet):
    queryset = Derogation.objects.all()
    serializer_class = DerogationSerializer
