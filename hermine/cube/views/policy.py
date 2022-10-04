#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView

from cube.forms import CreateLicenseChoiceForm, CreateLicenseCurationForm
from cube.models import LicenseChoice, Usage, LicenseCuration


class AbstractCreateUsageDecisionView(CreateView):
    usage = None

    def dispatch(self, request, *args, **kwargs):
        self.usage = get_object_or_404(Usage, id=kwargs["id"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usage"] = self.usage
        return kwargs

    def get_success_url(self):
        return reverse("cube:release_validation", kwargs={"pk": self.usage.release.id})


class CreateLicenseCurationView(AbstractCreateUsageDecisionView):
    model = LicenseCuration
    form_class = CreateLicenseCurationForm


class CreateLicenseChoiceView(AbstractCreateUsageDecisionView):
    model = LicenseChoice
    form_class = CreateLicenseChoiceForm
