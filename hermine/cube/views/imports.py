# SPDX-FileCopyrightText: 2022 Hermine-team <hermine@inno3.fr>
# SPDX-License-Identifier: AGPL-3.0-only

from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from cube.forms import ImportLicensesForm
from cube.utils.generics import handle_generics_json
from cube.utils.licenses import handle_licenses_json


@csrf_exempt
def upload_licenses_file(request):
    if request.method == "POST":
        form = ImportLicensesForm(request.POST, request.FILES)
        if form.is_valid():
            handle_licenses_json(request.FILES["file"])
            return redirect(request.META["HTTP_REFERER"])
    return redirect(request.META["HTTP_REFERER"])


def upload_generics_file(request):
    if request.method == "POST":
        handle_generics_json(request.FILES["file"])
        return redirect("cube:generics")

    return render(request, "cube/generic_list.html")
