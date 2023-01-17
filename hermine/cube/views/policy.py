#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView

from cube.models import (
    Derogation,
    LicenseChoice,
)
from cube.views.mixins import LicenseRelatedMixin, SaveAuthorMixin


class AuthorizedContextUpdateView(LoginRequiredMixin, SaveAuthorMixin, UpdateView):
    model = Derogation
    fields = (
        "scope",
        "component",
        "version",
        "linking",
        "modification",
        "exploitation",
        "justification",
    )

    def get_context_data(self, **kwargs):
        return super().get_context_data(license=self.object.license, **kwargs)

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])


class AuthorizedContextCreateView(
    LoginRequiredMixin, SaveAuthorMixin, LicenseRelatedMixin, CreateView
):
    model = Derogation
    fields = (
        "scope",
        "component",
        "version",
        "linking",
        "modification",
        "exploitation",
        "justification",
    )

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])


class DerogationListView(LoginRequiredMixin, ListView):
    model = Derogation
    context_object_name = "derogations"
    queryset = Derogation.objects.exclude(
        product=None,
        release=None,
    )


class LicenseChoiceListView(LoginRequiredMixin, ListView):
    model = LicenseChoice
    paginate_by = 50
    queryset = LicenseChoice.objects.filter(
        product__isnull=True,
        release__isnull=True,
        component__isnull=True,
        version__isnull=True,
    )
