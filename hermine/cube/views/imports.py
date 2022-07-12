# SPDX-FileCopyrightText: 2022 Hermine-team <hermine@inno3.fr>
# SPDX-License-Identifier: AGPL-3.0-only

from django.shortcuts import redirect, render

from cube.utils.generics import handle_generics_json


def upload_generics_file(request):
    if request.method == "POST":
        handle_generics_json(request.FILES["file"].read())
        return redirect("cube:generics")

    return render(request, "cube/generic_list.html")
