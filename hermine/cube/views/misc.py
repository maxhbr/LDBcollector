#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#  SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
#  SPDX-License-Identifier: AGPL-3.0-only


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from cube.models import License, Product, Component, Release, Generic
from cube.models.meta import ReleaseConsultation


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "cube/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["last_releases"] = (
            rc.release
            for rc in ReleaseConsultation.objects.filter(user=self.request.user)
            .prefetch_related("release")
            .order_by("-date")[:10]
        )
        context["products_count"] = Product.objects.all().count()
        context["releases_count"] = Release.objects.all().count()
        context["components_count"] = Component.objects.all().count()
        context["licenses_count"] = License.objects.all().count()
        context["generics_count"] = Generic.objects.all().count()
        kwargs.update(context)

        return kwargs


class AboutView(TemplateView):
    template_name = "cube/about.html"
