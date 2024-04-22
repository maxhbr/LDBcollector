#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.http import require_POST
from django.views.generic import (
    UpdateView,
    ListView,
    CreateView,
    TemplateView,
    DeleteView,
)

from cube.forms.release_validation import (
    CreateLicenseCurationForm,
    CreateAndsValidationForm,
    CreateLicenseChoiceForm,
    CreateDerogationForm,
)
from cube.models import (
    Release,
    Usage,
    LicenseCuration,
    LicenseChoice,
    Derogation,
    Exploitation,
)
from cube.utils.release_validation import update_validation_step, propagate_choices
from cube.utils.spdx import simplified
from cube.views import LicenseRelatedMixin
from cube.views.mixins import (
    SaveAuthorMixin,
    ReleaseContextMixin,
    QuerySuccessUrlMixin,
)


class ReleaseValidationView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView
):
    """
    Shows 4 validation steps for a release of a product:
    step 1 : checks that license metadata are present and correct
    step 2 : checks that no licenses expression is ambiguous
    step 3 : ensure all scopes have a defined exploitation
    step 4 : resolves choices in case of multi-licenses
    step 5 : checks that chosen licenses are compatible with policy and derogs
    """

    model = Release
    template_name = "cube/release_validation.html"
    permission_required = "cube.view_release"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "usage_set",
                "usage_set__version",
                "usage_set__version__component",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return {
            **context,
            **update_validation_step(self.object),
        }


class AbstractCreateUsageConditionView(
    LoginRequiredMixin, PermissionRequiredMixin, SaveAuthorMixin, CreateView
):
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


class AbstractResetCorrectedLicenseView(
    LoginRequiredMixin, PermissionRequiredMixin, UpdateView
):
    model = Usage
    fields = []
    permission_required = "cube.change_version"

    def form_valid(self, form):
        self.object.version.corrected_license = ""
        self.object.version.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())


# Step 1


class ReleaseLicenseCurationCreateView(AbstractCreateUsageConditionView):
    model = LicenseCuration
    form_class = CreateLicenseCurationForm
    template_name = "cube/release_licensecuration_create.html"
    permission_required = "cube.add_licensecuration"


class ReleaseCuratedLicensesView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "cube/release_curated_licenses.html"
    release = None
    context_object_name = "usages"
    permission_required = "cube.view_release"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["release"] = self.release
        return context

    def get_queryset(self):
        self.release = get_object_or_404(Release, pk=self.kwargs["id"])
        return (
            self.release.usage_set.all()
            .exclude(version__corrected_license="")
            .exclude(version__spdx_valid_license_expr=F("version__corrected_license"))
        )


@method_decorator(require_POST, "dispatch")
class UpdateLicenseCurationView(AbstractResetCorrectedLicenseView):
    def get_success_url(self):
        return reverse(
            "cube:release_curated_licenses", kwargs={"id": self.object.release.pk}
        )


# Step 2
class ReleaseAndsValidationCreateView(AbstractCreateUsageConditionView):
    model = LicenseCuration
    form_class = CreateAndsValidationForm
    permission_required = "cube.add_licensecuration"


class ReleaseAndsConfirmationView(PermissionRequiredMixin, TemplateView):
    template_name = "cube/release_ands_confirmation.html"
    release = None
    permission_required = "cube.view_release"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.release = get_object_or_404(Release, id=self.kwargs["id"])
        context["release"] = self.release
        usages = (
            self.release.usage_set.all()
            .exclude(version__corrected_license="")
            .exclude(version__spdx_valid_license_expr="")
        )
        context["confirmed_usages"] = [
            u
            for u in usages
            if u.version.corrected_license == u.version.spdx_valid_license_expr
            or u.version.corrected_license
            == simplified(u.version.spdx_valid_license_expr)
        ]

        context["corrected_usages"] = [
            u
            for u in usages
            if u.version.corrected_license
            != simplified(u.version.spdx_valid_license_expr)
        ]
        return context


@method_decorator(require_POST, "dispatch")
class ReleaseUpdateAndsValidationView(AbstractResetCorrectedLicenseView):
    def get_success_url(self):
        return reverse(
            "cube:release_ands_validations", kwargs={"id": self.object.release.pk}
        )


# Step 3


class ReleaseExploitationUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ReleaseContextMixin,
    UpdateView,
):
    model = Exploitation
    fields = ["exploitation"]
    template_name = "cube/release_exploitation_update.html"
    permission_required = "cube.change_release"

    def get_success_url(self, *args, **kwargs):
        return reverse("cube:release_summary", args=[self.release.id])


class ReleaseExploitationCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ReleaseContextMixin,
    QuerySuccessUrlMixin,
    CreateView,
):
    model = Exploitation
    fields = ["project", "scope", "exploitation"]
    template_name = "cube/release_exploitation_create.html"
    permission_required = "cube.change_release"

    def get_initial(self):
        scope = self.request.GET.get("scope", "Default scope")
        project = self.request.GET.get("project", "Default project")
        return {"project": project, "scope": scope}

    def form_valid(self, form):
        form.instance.release = self.release
        return super().form_valid(form)

    def get_default_success_url(self):
        return reverse("cube:release_summary", args=[self.release.id])


class ReleaseExploitationDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, ReleaseContextMixin, DeleteView
):
    model = Exploitation
    template_name = "cube/release_exploitation_confirm_delete.html"
    permission_required = "cube.change_release"

    def get_success_url(self, *args, **kwargs):
        return reverse("cube:release_summary", args=[self.release.id])


# Step 4


class ReleaseLicenseChoiceCreateView(AbstractCreateUsageConditionView):
    model = LicenseChoice
    template_name = "cube/release_licensechoice_create.html"
    form_class = CreateLicenseChoiceForm
    permission_required = "cube.add_licensechoice"


class ReleaseLicenseChoiceListView(
    LoginRequiredMixin, PermissionRequiredMixin, ReleaseContextMixin, ListView
):
    template_name = "cube/release_choices.html"
    release = None
    context_object_name = "usages"
    permission_required = "cube.view_release"

    def get_queryset(self):
        return propagate_choices(self.release)["resolved"]


@method_decorator(require_POST, "dispatch")
class ReleaseUpdateLicenseChoiceView(
    LoginRequiredMixin, PermissionRequiredMixin, UpdateView
):
    model = Usage
    fields = []
    permission_required = "cube.change_release"

    def form_valid(self, form):
        self.object.license_expression = ""
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "cube:release_licensechoice_list", kwargs={"id": self.object.release.pk}
        )


# Step 5


class ReleaseDerogationCreateView(
    LicenseRelatedMixin, AbstractCreateUsageConditionView
):
    model = Derogation
    form_class = CreateDerogationForm
    permission_required = "cube.add_derogation"
    template_name = "cube/release_derogation_create.html"
