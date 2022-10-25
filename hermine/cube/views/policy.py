#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from cube.forms import (
    CreateLicenseChoiceForm,
    CreateLicenseCurationForm,
    DerogationForm,
    CreateExpressionValidationForm,
)
from cube.models import (
    LicenseChoice,
    Usage,
    LicenseCuration,
    Derogation,
    License,
    ExpressionValidation,
)
from cube.views.mixins import LicenseRelatedMixin


class AbstractCreateUsageConditionView(LoginRequiredMixin, CreateView):
    usage = None

    def dispatch(self, request, *args, **kwargs):
        self.usage = get_object_or_404(Usage, id=kwargs["usage_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usage"] = self.usage
        return kwargs

    def get_success_url(self):
        return reverse("cube:release_validation", kwargs={"pk": self.usage.release.id})


class CreateLicenseCurationView(AbstractCreateUsageConditionView):
    model = LicenseCuration
    form_class = CreateLicenseCurationForm
    template_name_suffix = "_create"


class CreateExpressionValidationView(AbstractCreateUsageConditionView):
    model = ExpressionValidation
    form_class = CreateExpressionValidationForm


class CreateLicenseChoiceView(AbstractCreateUsageConditionView):
    model = LicenseChoice
    form_class = CreateLicenseChoiceForm


class DerogationUsageContextCreateView(
    LicenseRelatedMixin, AbstractCreateUsageConditionView
):
    model = Derogation
    form_class = DerogationForm


class DerogationUpdateView(LoginRequiredMixin, UpdateView):
    model = Derogation
    fields = ("linking", "scope")

    def get_context_data(self, **kwargs):
        return super().get_context_data(license=self.object.license, **kwargs)

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])


class DerogationLicenseContextCreateView(
    LoginRequiredMixin, LicenseRelatedMixin, CreateView
):
    model = Derogation
    fields = ("linking", "scope")

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])
