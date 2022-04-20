# SPDX-FileCopyrightText: 2022 Hermine-team <hermine@inno3.fr>
# SPDX-License-Identifier: AGPL-3.0-only

from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from cube.forms import ImportLicensesForm, ImportBomForm
from cube.importers import import_ort_evaluated_model_json_file, import_spdx_file
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


def import_bom(request):
    form = ImportBomForm(request.POST, request.FILES)
    status = None
    if form.is_valid():
        status = "success"
        try:
            if form.cleaned_data["bom_type"] == "ORTBom":
                import_ort_evaluated_model_json_file(
                    request.FILES["file"], form.cleaned_data["release"].id
                )
            elif form.cleaned_data["bom_type"] == "SPDXBom":
                import_spdx_file(request.FILES["file"], form.cleaned_data["release"].id)
        except:  # noqa: E722 TODO
            print("The file you chose do not match the format you chose.")
            status = "error"

        return render(
            request,
            "cube/import_bom.html",
            {
                "form": form,
                "status": status,
                "release_id": form.cleaned_data["release"].id,
            },
        )
    else:
        form = ImportBomForm()
        return render(request, "cube/import_bom.html", {"form": form, "status": status})
