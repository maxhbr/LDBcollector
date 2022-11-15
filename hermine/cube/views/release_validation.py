#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.http import require_POST
from django.views.generic import UpdateView, ListView, CreateView, TemplateView

from cube.forms.release_validation import (
    CreateLicenseCurationForm,
    CreateExpressionValidationForm,
    CreateLicenseChoiceForm,
    CreateDerogationForm,
)
from cube.models import (
    Release,
    Usage,
    LicenseCuration,
    ExpressionValidation,
    LicenseChoice,
    Derogation,
)
from cube.utils.releases import update_validation_step, propagate_choices
from cube.views import LicenseRelatedMixin


class ReleaseValidationView(LoginRequiredMixin, generic.DetailView):
    """
    Shows 4 validation steps for a release of a product:
    step 1 : checks that license metadata are present and correct
    step 2 : checks that all licenses have been reviewed by legal dpt
    step 3 : resolves choices in case of multi-licenses
    step 4 : checks that chosen licenses are compatible with policy and derogs
    """

    model = Release
    template_name = "cube/release.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "usage_set",
                "usage_set__version",
                "usage_set__version__component",
                "usage_set__licenses_chosen",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return {
            **context,
            **update_validation_step(self.object),
        }


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


# Step 1


class ReleaseLicenseCurationCreateView(AbstractCreateUsageConditionView):
    model = LicenseCuration
    form_class = CreateLicenseCurationForm
    template_name_suffix = "_create"


class ReleaseCuratedLicensesListView(ListView):
    template_name = "cube/release_curated_licenses.html"
    release = None
    context_object_name = "usages"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["release"] = self.release
        return context

    def get_queryset(self):
        self.release = get_object_or_404(Release, pk=self.kwargs["id"])
        return (
            self.release.usage_set.all()
            .exclude(version__spdx_valid_license_expr="")
            .exclude(
                version__spdx_valid_license_expr=F("version__declared_license_expr")
            )
        )


@method_decorator(require_POST, "dispatch")
class UpdateLicenseCurationView(UpdateView):
    model = Usage
    fields = []

    def form_valid(self, form):
        self.object.version.spdx_valid_license_expr = ""
        self.object.version.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("cube:release_validation", kwargs={"pk": self.object.release.pk})


# Step 3


class ReleaseExpressionValidationCreateView(AbstractCreateUsageConditionView):
    model = ExpressionValidation
    form_class = CreateExpressionValidationForm


class ReleaseExpressionValidationListView(TemplateView):
    template_name = "cube/release_expression_validations.html"
    release = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.release = get_object_or_404(Release, id=self.kwargs["id"])
        context["release"] = self.release
        usages = self.release.usage_set.all().exclude(version__corrected_license="")
        context["confirmed_usages"] = usages.filter(
            version__corrected_license=F("version__spdx_valid_license_expr")
        )
        context["corrected_usages"] = usages.exclude(
            version__corrected_license=F("version__spdx_valid_license_expr")
        )
        return context


@method_decorator(require_POST, "dispatch")
class UpdateExpressionValidationView(UpdateView):
    model = Usage
    fields = []

    def form_valid(self, form):
        self.object.version.corrected_license = ""
        self.object.version.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("cube:release_validation", kwargs={"pk": self.object.release.pk})


# Step 4


class ReleaseLicenseChoiceCreateView(AbstractCreateUsageConditionView):
    model = LicenseChoice
    form_class = CreateLicenseChoiceForm


class ReleaseLicenseChoiceListView(ListView):
    template_name = "cube/release_choices.html"
    release = None
    context_object_name = "usages"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["release"] = self.release
        return context

    def get_queryset(self):
        self.release = get_object_or_404(Release, pk=self.kwargs["id"])
        return propagate_choices(self.release)["resolved"]


@method_decorator(require_POST, "dispatch")
class UpdateLicenseChoiceView(UpdateView):
    model = Usage
    fields = []

    def form_valid(self, form):
        self.object.license_expression = ""
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("cube:release_validation", kwargs={"pk": self.object.release.pk})


class ReleaseDerogationCreateView(
    LicenseRelatedMixin, AbstractCreateUsageConditionView
):
    model = Derogation
    form_class = CreateDerogationForm
