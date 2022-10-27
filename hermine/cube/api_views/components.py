#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from rest_framework import viewsets

from cube.models import Usage, Component, Version
from cube.serializers import UsageSerializer, VersionSerializer, ComponentSerializer


class UsageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows usages to be viewed or edited
    The list can be optionally restricted to the usages of a given release,
    by provideing a `release` query parameter in the URL.
    """

    serializer_class = UsageSerializer

    def get_queryset(self):
        queryset = Usage.objects.all()
        release = self.request.query_params.get("release")
        if release is not None:
            queryset = queryset.filter(release=release)
        return queryset


class ComponentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows components to be viewed or edited
    """

    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    lookup_field = "pk"


class VersionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows versions to be viewed or edited.
    """

    queryset = Version.objects.all()

    def get_queryset(self):
        """
        Handles if the user is accessing the viewset from root of api or from a nested
        componentset in a license


        :return: All the versions if query is made from /api/versions/, or only the
            relevant version if query is made from
            /api/components/<int: componen_id>/versions
        :rtype: QuerySet
        """
        qs = super().get_queryset()

        if component := self.kwargs.get("nested_1_pk") is not None:
            qs = qs.filter(component=component)

        return qs

    def perform_create(self, serializer):
        serializer.save(component_id=self.kwargs.get("nested_1_pk"))

    serializer_class = VersionSerializer
    lookup_field = "id"
