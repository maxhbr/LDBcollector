#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#  SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
#  SPDX-License-Identifier: AGPL-3.0-only

#
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from cube.models import License, Product, Component, Release


@login_required
def index(request):

    latest_license_list = License.objects.filter(status="Tocheck").annotate(
        Count("obligation")
    )
    nb_products = Product.objects.all().count()
    nb_releases = Release.objects.all().count()
    nb_components = Component.objects.all().count()
    nb_licenses = License.objects.all().count()

    context = {
        "latest_license_list": latest_license_list,
        "nb_products": nb_products,
        "nb_releases": nb_releases,
        "nb_components": nb_components,
        "nb_licenses": nb_licenses,
    }
    return render(request, "cube/index.html", context)


def about(request):
    context = {}
    return render(request, "cube/about.html", context)
