#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView

from cube.forms.policy import LicenseChoiceCreateForm, LicenseChoiceUpdateForm
from cube.models import (
    Derogation,
    LicenseChoice,
)
from cube.views.mixins import LicenseRelatedMixin, SaveAuthorMixin, QuerySuccessUrlMixin


class AuthorizedContextListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    queryset = Derogation.objects.filter(product=None, release=None)
    permission_required = "cube.view_derogation"
    template_name = "cube/authorized_context_list.html"
    context_object_name = "authorized_contexts"


class AuthorizedContextUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SaveAuthorMixin,
    QuerySuccessUrlMixin,
    UpdateView,
):
    permission_required = "cube.change_derogation"
    model = Derogation
    template_name = "cube/derogation_form.html"
    fields = (
        "linking",
        "modification",
        "exploitation",
        "scope",
        "category",
        "justification",
    )
    success_url = reverse_lazy("cube:authorized_context_list")

    def get_context_data(self, **kwargs):
        return super().get_context_data(license=self.object.license, **kwargs)


class AuthorizedContextCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SaveAuthorMixin,
    LicenseRelatedMixin,
    CreateView,
):
    permission_required = "cube.add_derogation"
    model = Derogation
    fields = (
        "linking",
        "modification",
        "exploitation",
        "scope",
        "category",
        "justification",
    )

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])


class DerogationListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "cube.view_derogation"
    model = Derogation
    context_object_name = "derogations"
    queryset = Derogation.objects.exclude(
        product=None,
        release=None,
    )


class LicenseChoiceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "cube.view_licensechoice"
    model = LicenseChoice
    template_name = "cube/licensechoice_list.html"
    paginate_by = 50
    queryset = LicenseChoice.objects.filter(
        product__isnull=True,
        release__isnull=True,
        component__isnull=True,
        version__isnull=True,
        scope="",
        exploitation="",
    )


class LicenseChoiceEditView(
    LoginRequiredMixin, PermissionRequiredMixin, QuerySuccessUrlMixin, UpdateView
):
    permission_required = "cube.change_licensechoice"
    model = LicenseChoice
    template_name = "cube/licensechoice_edit.html"
    form_class = LicenseChoiceUpdateForm
    success_url = reverse_lazy("cube:licensechoices")


class LicenseChoiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "cube.add_licensechoice"
    model = LicenseChoice
    template_name = "cube/licensechoice_create.html"
    form_class = LicenseChoiceCreateForm

    def get_success_url(self):
        return reverse("cube:licensechoice_list")
