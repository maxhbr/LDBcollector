# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

import json

from django.http import HttpResponse
from django.views import View

from cube.models import License, LicenseCuration
from cube.serializers import LicenseSerializer
from cube.utils.licenses import export_licenses as export_licenses_json
from cube.utils.generics import export_generics as export_generics_json
from cube.utils.ort import export_curations


class BaseExportFileView(View):
    filename = None
    content_type = "application/json"

    def get_filename(self):
        return self.filename

    def get_data(self):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        response = HttpResponse(self.get_data(), content_type=self.content_type)
        response["Content-Disposition"] = (
            "attachment; filename=%s" % self.get_filename()
        )
        return response


class ExportLicensesView(BaseExportFileView):
    filename = "licenses.json"

    def get_data(self):
        return export_licenses_json(indent=True)


class Export1LicenseView(BaseExportFileView):
    license_instance = None

    def get_filename(self):
        return self.license_instance.spdx_id + ".json"

    def get_data(self):
        data = LicenseSerializer(self.license_instance).data
        return json.dumps(data, indent=4)

    def get(self, request, *args, **kwargs):
        self.license_instance = License.objects.get(id=kwargs["license_id"])
        return super().get(request, kwargs["license_id"])


class ExportGenericsView(BaseExportFileView):
    filename = "generics.json"

    def get_data(self):
        return export_generics_json()


class ExportLicenseCurationsView(BaseExportFileView):
    filename = "ort_curations.yaml"
    content_type = "application/x-yaml"

    def get_data(self):
        return export_curations(LicenseCuration.objects.all())
