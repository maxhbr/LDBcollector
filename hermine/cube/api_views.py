# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

import json

from rest_framework import viewsets
from rest_framework.response import Response
from cube.serializers import (
    LicenseSerializer,
    ObligationSerializer,
    GenericSerializer,
    UsageSerializer,
    ProductSerializer,
    ReleaseSerializer,
    ComponentSerializer,
    VersionSerializer,
    UploadSPDXSerializer,
    DerogationSerializer,
    UploadORTSerializer,
)

from .models import (
    Product,
    Release,
    Usage,
    License,
    Obligation,
    Generic,
    Component,
    Version,
)

from .utils.licenses import (
    check_licenses_against_policy,
    get_licenses_to_check_or_create,
)
from .views import propagate_choices

from .importers import import_ort_evaluated_model_json_file, import_spdx_file


class RootViewSet(viewsets.ViewSet):
    """
    This is the root of the API.
    Here is the list of API endpoints you can use:

    - api/components/
    - api/components/<int:component_id>/versions/
    - api/generics/
    - api/licenses/
    - api/licenses/<int:license_id>/obligations/
    - api/obligations/
    - api/products/
    - api/products/<int:product_id>/releases/
    - api/releases/
    - api/releases/<int:release_id>/validation-1/
    - api/releases/<int:release_id>/validation-2/
    - api/releases/<int:release_id>/validation-3/
    - api/releases/<int:release_id>/validation-4/
    - api/upload_ort
    - api/usages/

    """

    def list(self, request):
        return Response("Feel free to use the API")


class LicenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows licenses to be viewed or edited.
    """

    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    lookup_field = "id"

    def pre_save(self, obj):
        # https://docs.djangoproject.com/fr/3.2/ref/signals/#pre-save
        obj.samplesheet = self.request.FILES.get("file")


class UsageViewSet(viewsets.ModelViewSet):
    queryset = Usage.objects.all()
    serializer_class = UsageSerializer


class GenericViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows generic obligations to be viewed or edited.
    """

    queryset = Generic.objects.all()
    serializer_class = GenericSerializer
    lookup_field = "id"


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"

    def pre_save(self, obj):
        # https://docs.djangoproject.com/fr/3.2/ref/signals/#pre-save
        obj.samplesheet = self.request.FILES.get("file")


class ReleaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows releases to be viewed or edited.
    """

    serializer_class = ReleaseSerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        Handles if the user is accessing the viewset from root of api or from a nested
        # ReleaseSet in a product (api/products/<int:product_id>/releases)

        :return: Set of Release objects
        :rtype: QuerySet
        """
        # This kwargs should be id, not name_id

        product_id = self.kwargs.get("name_id")
        if product_id is None:
            response = Release.objects.all()
        else:
            response = Release.objects.filter(product__id=product_id)

        return response


class UploadSPDXViewSet(viewsets.ViewSet):
    """
    API endpoint that allows to upload an SPDX file to Hermine.
    """

    serializer_class = UploadSPDXSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def list(self, request):
        return Response("GET Upload SPDX API")

    def put(self, request):
        spdx_file = request.FILES.get("spdx_file")
        release_id = request.POST.get("release_id")
        content_type = spdx_file.content_type
        import_spdx_file(spdx_file, release_id)
        response = "POST API and you have uploaded a {} file".format(content_type)
        return Response(response)


class UploadORTViewSet(viewsets.ViewSet):
    """
    API endpoint that allows to upload an ORT output file to Hermine.
    """

    serializer_class = UploadORTSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def list(self, request):
        return Response("GET Upload SPDX API")

    def put(self, request):
        ort_file = request.FILES.get("ort_file")
        release_id = request.POST.get("release_id")
        if ort_file is not None:
            content_type = ort_file.content_type
            import_ort_evaluated_model_json_file(ort_file, release_id)
            response = "POST API and you have uploaded a {} file".format(content_type)
        else:
            response = "You forgot to upload a file !"
        return Response(response)


class ComponentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows components to be viewed or edited
    """

    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    lookup_field = "pk"

    def pre_save(self, obj):
        # https://docs.djangoproject.com/fr/3.2/ref/signals/#pre-save
        obj.samplesheet = self.request.FILES.get("file")


class VersionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows versions to be viewed or edited.
    """

    def get_queryset(self):
        """
        Handles if the user is accessing the viewset from root of api or from a nested
        componentset in a license


        :return: All the versions if query is made from /api/versions/, or only the
            relevant version if query is made from
            /api/components/<int: componen_id>/versions
        :rtype: QuerySet
        """
        component = self.kwargs.get("nested_1_pk")
        return (
            Version.objects.all()
            if component is None
            else Version.objects.filter(component__id=component)
        )

    serializer_class = VersionSerializer
    lookup_field = "id"


class ObligationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows licenses to be viewed or edited.
    """

    def get_queryset(self):
        """
        Handles if the user is accessing the viewset from root of api or from a nested
        obligationset in a license


        :return: [description]
        :rtype: [type]
        """
        license = self.kwargs.get("id_id")
        return (
            Obligation.objects.all()
            if license is None
            else Obligation.objects.filter(license__id=license)
        )

    serializer_class = ObligationSerializer
    lookup_field = "id"


# API VALIDATION STEP - 1
class UnnormalisedUsagesViewSet(viewsets.ViewSet):
    """
    API endpoint that allows to know if the Unnormalised Usages (Validation Step 1)
    Can be found at 'api/releases/52/validation-1/'
    """

    def list(self, request, **kwargs):
        response = {}

        # This kwargs has a strange name, it's DRF fault
        release = json.loads(kwargs["nested_1_id"])
        try:
            release = Release.objects.get(pk=release)
        except Release.DoesNotExist:
            return Response("No Release matching this ID")

        unnormalised_usages = release.usage_set.all().filter(
            version__spdx_valid_license_expr="", version__corrected_license=""
        )
        s = UsageSerializer(unnormalised_usages, many=True)

        response["unnormalised_usages"] = s.data

        if len(s.data) > 0:
            response["valid"] = False
        else:
            response["valid"] = True
        return Response(response)


# API VALIDATION STEP - 2
class LicensesToCheckViewSet(viewsets.ViewSet):
    """
    API endpoint that allows to know the Licenses that need to be checked or created
    (Validation Step 2)

    Can be found at 'api/releases/52/validation-2/'
    """

    def list(self, request, **kwargs):
        response = {}
        # This kwargs has a strange name, it's DRF fault
        release = json.loads(kwargs["nested_1_id"])
        try:
            release = Release.objects.get(pk=release)
        except Release.DoesNotExist:
            return Response("No Release matching this ID")

        licenses = get_licenses_to_check_or_create(release)
        for field, value in licenses.items():
            try:
                s = LicenseSerializer(value, many=True)
                response[field] = s.data
            except AttributeError:
                response = "There was an error while serializing " + field
        if len(response["licenses_to_check"]) + len(response["licenses_to_create"]) > 0:
            response["valid"] = False
        else:
            response["valid"] = True
        return Response(response)


# API VALIDATION STEP - 3
class LicensesUsagesViewSet(viewsets.ViewSet):
    """
    API endpoint that allows to know if every License Usage have been specified for
    complex SPDX expressions -i.a. the ones that have more than 1 SPDX identifier in
    it- (Validation Step 3)

    Can be found at 'api/releases/52/validation-3/'
    """

    def list(self, request, **kwargs):
        response = {}
        # This kwargs has a strange name, it's DRF fault
        release = json.loads(kwargs["nested_1_id"])
        usages = propagate_choices(release)
        for field, value in usages.items():
            try:
                s = UsageSerializer(value, many=True)
                response[field] = s.data
            except AttributeError:
                response = "There was an error while serializing " + field
        if len(response["to_resolve"]) > 0:
            response["valid"] = False
        else:
            response["valid"] = True
        return Response(response)


# API VALIDATION STEP - 4
class LicensesAgainstPolicyViewSet(viewsets.ViewSet):
    """
    API endpoint that allows to know the Licenses that need or have a derogation
    (Validation Step 4).

    5 fields are populated with different models
    `usages_lic_red` : Usage
    `usages_lic_orange` : Usage
    `usages_lic_grey` : Usage
    `involved_lic` : License
    `derogations` : Derogation
    Can be found at 'api/releases/52/validation-4/'
    """

    def list(self, request, **kwargs):
        response = {}
        # This kwargs has a strange name, it's DRF fault
        release = json.loads(kwargs["nested_1_id"])
        try:
            release = Release.objects.get(pk=release)
        except Release.DoesNotExist:
            return Response("No Release matching this ID")

        r = check_licenses_against_policy(release)
        for field, value in r.items():
            try:
                if field.startswith("usages_"):
                    s = UsageSerializer(value, many=True)
                    response[field] = s.data

                elif field.startswith("involved_"):
                    s = LicenseSerializer(value, many=True)
                    response[field] = s.data

                elif field.startswith("derogations"):
                    s = DerogationSerializer(value, many=True)
                    response[field] = s.data

            except AttributeError:
                response = "There was an error while serializing " + field

        if (
            len(response["usages_lic_red"])
            + len(response["usages_lic_orange"])
            + len(response["usages_lic_grey"])
            > 0
        ):
            response["valid"] = False
        else:
            response["valid"] = True
        return Response(response)
