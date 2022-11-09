#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView

from cube.models import (
    Derogation,
)
from cube.views.mixins import LicenseRelatedMixin


class DerogationUpdateView(LoginRequiredMixin, UpdateView):
    model = Derogation
    fields = ("linking", "scope")

    def get_context_data(self, **kwargs):
        return super().get_context_data(license=self.object.license, **kwargs)

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])


class DerogationCreateView(LoginRequiredMixin, LicenseRelatedMixin, CreateView):
    model = Derogation
    fields = ("linking", "scope")

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])


class DerogationListView(LoginRequiredMixin, ListView):
    model = Derogation
    context_object_name = "derogations"
    template_name = "cube/derogation_list.html"
    queryset = Derogation.objects.exclude(
        component__isnull=True,
        version__isnull=True,
        product__isnull=True,
        release__isnull=True,
    )
