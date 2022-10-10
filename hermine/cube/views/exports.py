# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

import json

from django.http import HttpResponse
from django.views import View

from cube.models import License
from cube.serializers import LicenseSerializer
from cube.utils.licenses import export_licenses as export_licenses_json
from cube.utils.generics import export_generics as export_generics_json


class ExportLicensesView(View):
    def get(self, request):
        """Calls API to retrieve list of licenses. Handles DRF pagination.

        :return: HttpResponse that triggers the download of a JSON file containing every
            license in a JSON Array.
        :rtype: DjangoHttpResponse
        """
        filename = "licenses.json"
        data = export_licenses_json(indent=True)
        response = HttpResponse(data, content_type="application/json")
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


class Export1LicenseView(View):
    def get(self, request, license_id):
        license_instance = License.objects.get(id=license_id)
        filename = license_instance.spdx_id + ".json"
        data = LicenseSerializer(license_instance).data
        response = HttpResponse(
            json.dumps(data, indent=4), content_type="application/json"
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


class ExportGenericsView(View):
    def get(self, request):
        filename = "generics.json"
        data = export_generics_json()
        response = HttpResponse(
            data,
            content_type="application/json",
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response
