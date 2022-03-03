# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

import json

import requests
from django.conf import settings
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from cube.models import License, Generic
from cube.serializers import LicenseSerializer


def export_licenses(request):
    """Calls API to retrieve list of licenses. Handles DRF pagination.

    :return: HttpResponse that triggers the download of a JSON file containing every
        license in a JSON Array.
    :rtype: DjangoHttpResponse
    """
    request_uri = settings.API_BASE_URL + "licenses/?format=json"
    filename = "licenses.json"
    with open(filename, "w+"):
        r = requests.get(request_uri)
        json_r = r.json()
        licenseJSONArray = json_r["results"]
        while json_r["next"]:
            r = requests.get(json_r["next"])
            json_r = r.json()
            for license in json_r["results"]:
                licenseJSONArray.append(license)
        response = HttpResponse(
            json.dumps(licenseJSONArray, indent=4), content_type="application/json"
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


def export_specific_license(request, license_id):
    license_instance = License.objects.get(id=license_id)
    filename = license_instance.spdx_id + ".json"
    serializer = LicenseSerializer
    data = serializer(license_instance).data
    with open(filename, "w+"):
        response = HttpResponse(
            json.dumps(data, indent=4), content_type="application/json"
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


def export_generics(request):
    filename = "generics.json"
    with open(filename, "w+"):
        response = HttpResponse(
            serialize("json", Generic.objects.all(), cls=DjangoJSONEncoder),
            content_type="application/json",
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response