# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F
from django.forms import Form, ChoiceField, Select
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views import generic
from django.views.decorators.http import require_POST
from django.views.generic import UpdateView, DetailView, ListView

from cube.forms import ImportBomForm
from cube.importers import (
    import_ort_evaluated_model_json_file,
    import_spdx_file,
    SBOMImportFailure,
)
from cube.models import (
    Release,
    Usage,
    Generic,
    Derogation,
    Exploitation,
)
from cube.utils.licenses import (
    get_usages_obligations,
)
from cube.utils.releases import update_validation_step

logger = logging.getLogger(__name__)


class ReleaseView(LoginRequiredMixin, generic.DetailView):
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


class ReleaseBomView(LoginRequiredMixin, UpdateView):
    model = Release
    form_class = ImportBomForm
    context_object_name = "release"
    template_name = "cube/release_bom.html"

    def get_success_url(self):
        return reverse("cube:release_bom", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        replace = form.cleaned_data["import_mode"] == ImportBomForm.IMPORT_MODE_REPLACE
        try:
            if form.cleaned_data["bom_type"] == ImportBomForm.BOM_ORT:
                import_ort_evaluated_model_json_file(
                    self.request.FILES["file"],
                    self.object.pk,
                    replace,
                    linking=form.cleaned_data.get("linking"),
                )
            elif form.cleaned_data["bom_type"] == ImportBomForm.BOM_SPDX:
                import_spdx_file(
                    self.request.FILES["file"],
                    self.object.pk,
                    replace,
                    linking=form.cleaned_data.get("linking"),
                )
        except SBOMImportFailure as e:
            form.add_error(None, e)
            return super().form_invalid(form)

        messages.add_message(
            self.request,
            messages.SUCCESS,
            mark_safe(
                f"""
                You successfully uploaded your file.
                Go check the validation steps you need to achieve at the relevant
                <b><a href="{reverse("cube:release_validation", kwargs={"pk": self.object.id})}"> release page</a></b>.
                """
            ),
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class ReleaseObligView(LoginRequiredMixin, generic.DetailView):
    """
    Lists relevant obligations for a given release
    """

    model = Release
    template_name = "cube/release_oblig.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usages = self.object.usage_set.all()
        generics_involved, orphaned_licenses = get_usages_obligations(usages)
        context["generics_involved"] = generics_involved
        context["orphaned_licenses"] = orphaned_licenses

        return context


@login_required
def release_generic(request, release_id, generic_id):
    usages = Usage.objects.filter(
        release__id=release_id, licenses_chosen__obligation__generic__id=generic_id
    )
    generic = Generic.objects.get(pk=generic_id)
    release = Release.objects.get(pk=release_id)
    context = {"usages": usages, "generic": generic, "release": release}
    return render(request, "cube/release_generic.html", context)


class ReleaseExploitationForm(Form):
    def __init__(self, instance, *args, **kwargs):
        self.release = instance
        self.scopes = self.release.usage_set.values_list("project", "scope").annotate(
            count=Count("*")
        )
        super().__init__(*args, **kwargs)

        for project, scope, count in self.scopes:
            self.fields[project + scope] = ChoiceField(
                choices=Usage.EXPLOITATION_CHOICES,
                widget=Select(attrs={"class": "select"}),
                label=f"{project or '(project undefined)'} - {scope} ({count} components)",
            )

            try:
                self.initial[project + scope] = self.release.exploitations.get(
                    project=project, scope=scope
                ).exploitation
            except Exploitation.DoesNotExist:
                pass

    def save(self):
        for project, scope, _ in self.scopes:
            exploitation_type = self.cleaned_data[project + scope]
            Exploitation.objects.update_or_create(
                release=self.release,
                project=project,
                scope=scope,
                defaults={"exploitation": exploitation_type},
            )

        return self.release


class ReleaseSummaryView(LoginRequiredMixin, UpdateView):
    model = Release
    context_object_name = "release"
    template_name = "cube/release_summary.html"
    form_class = ReleaseExploitationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.pop("form")
        context["exploitation_form"] = [  # only way to loop properly
            {
                "project": project,
                "scope": scope,
                "count": count,
                "field": form[f"{project}{scope}"],
            }
            for (project, scope, count) in form.scopes
        ]
        context["bom_form"] = ImportBomForm()

        return context

    def get_success_url(self):
        return reverse("cube:release_summary", args=[self.object.pk])


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
        return reverse("cube:release_summary", kwargs={"pk": self.object.release.pk})


@login_required
def release_add_derogation(request, release_id, usage_id):
    """Takes the user to the page that allows them to add a derogation for the release
    they're working on.

    :param request: mandatory
    :type request: HttpRequest
    :param release_id: The id of this release
    :type release_id: django AutoField
    :param usage_id: The id of this usage
    :type usage_id: django AutoField
    :return: Renders the context into the template.
    :rtype: HttpResponse
    """
    usage = Usage.objects.get(pk=usage_id)
    release = Release.objects.get(pk=release_id)
    context = {"usage": usage, "release": release}
    return render(request, "cube/release_derogation.html", context)


@login_required
def release_send_derogation(request, release_id, usage_id):
    """Digests inputs from the associated form and send it to the database.

    :param request: mandatory
    :type request: HttpRequest
    :param release_id: The id of this release
    :type release_id: django AutoField
    :param usage_id: The id of this usage
    :type usage_id: django AutoField
    :return: A redirection to this release main page.
    :rtype: HttpResponseRedirect
    """
    actionvalue = request.POST["action"]
    justificationvalue = request.POST["justification"]
    usage_derog = linking = scope = None
    usage = get_object_or_404(Usage, pk=usage_id)
    release = get_object_or_404(Release, pk=release_id)
    for license in usage.licenses_chosen.all():
        if actionvalue == "component":
            usage_derog = usage
        if actionvalue == "linking":
            linking = usage.linking
        if actionvalue == "scope":
            scope = usage.scope
        if actionvalue == "linkingscope":
            scope = usage.scope
            linking = usage.linking

        derogation = Derogation(
            release=release,
            usage=usage_derog,
            license=license,
            scope=scope,
            justification=justificationvalue,
            linking=linking,
        )
        derogation.save()

    response = redirect("cube:release_validation", release_id)
    return response


class ReleaseFixedLicensesList(ListView):
    template_name = "cube/release_fixed_licenses.html"
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
