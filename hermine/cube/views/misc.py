#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#  SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
#  SPDX-License-Identifier: AGPL-3.0-only

#
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import render
from django.views.generic import TemplateView

from cube.models import License, Product, Component, Release


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "cube/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["latest_license_list"] = License.objects.filter(
            status="Tocheck"
        ).annotate(Count("obligation"))
        context["nb_products"] = Product.objects.all().count()
        context["nb_releases"] = Release.objects.all().count()
        context["nb_components"] = Component.objects.all().count()
        context["nb_licenses"] = License.objects.all().count()
        kwargs.update(context)

        return kwargs


class AboutView(LoginRequiredMixin, TemplateView):
    template_name = "cube/about.html"


def about(request):
    context = {}
    return render(request, "cube/about.html", context)
