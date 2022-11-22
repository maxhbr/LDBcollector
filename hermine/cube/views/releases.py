# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
import csv
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.forms import Form, ChoiceField, Select
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.views import generic
from django.views.generic import UpdateView, DetailView, TemplateView

from cube.forms.importers import ImportBomForm
from cube.importers import (
    import_ort_evaluated_model_json_file,
    import_spdx_file,
    SBOMImportFailure,
)
from cube.models import (
    Release,
    Usage,
    Generic,
    Exploitation,
)
from cube.utils.licenses import (
    get_usages_obligations,
)
from cube.views.mixins import SearchMixin

logger = logging.getLogger(__name__)


class ReleaseImportView(LoginRequiredMixin, UpdateView):
    model = Release
    form_class = ImportBomForm
    context_object_name = "release"
    template_name = "cube/release_import.html"

    def get_success_url(self):
        return reverse("cube:release_import", kwargs={"pk": self.object.pk})

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
                You can add components from another source or check the validation steps you need to achieve in the
                <b><a href="{reverse("cube:release_validation", kwargs={"pk": self.object.id})}"> Validation tab</a></b>.
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


class ReleaseGenericView(LoginRequiredMixin, TemplateView):
    template_name = "cube/release_generic.html"

    def get_context_data(self, **kwargs):
        usages = Usage.objects.filter(
            release__id=self.kwargs["release_id"],
            licenses_chosen__obligation__generic__id=self.kwargs["generic_id"],
        )
        generic = Generic.objects.get(pk=self.kwargs["generic_id"])
        release = Release.objects.get(pk=self.kwargs["release_id"])
        return {"usages": usages, "generic": generic, "release": release}


class ReleaseExploitationForm(Form):
    def __init__(self, instance: Release, *args, **kwargs):
        self.release = instance
        self.scopes = self.release.usage_set.values_list("project", "scope").annotate(
            count=Count("*")
        )
        super().__init__(*args, **kwargs)

        for project, scope, count in self.scopes:
            self.fields[str(project) + str(scope)] = ChoiceField(
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


class ReleaseBomExportView(LoginRequiredMixin, DetailView):
    model = Release

    def get(self, request, **kwargs):
        self.object = self.get_object()
        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{slugify(self.object)}.csv"'
            },
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "sub_project",
                "scope",
                "name",
                "version",
                "purl",
                "declared_license_expr",
                "normalized_license",
                "corrected_license",
                "applicable license",
                "modified",
                "exploitation",
                "linking type",
            ]
        )

        for usage in self.object.usage_set.all():
            writer.writerow(
                [
                    usage.project,
                    usage.scope,
                    usage.version.component.name,
                    usage.version.version_number,
                    usage.version.purl,
                    usage.version.declared_license_expr,
                    usage.version.spdx_valid_license_expr,
                    usage.version.corrected_license,
                    usage.license_expression,
                    usage.component_modified,
                    usage.exploitation,
                    usage.linking,
                ]
            )
        return response


class UsageListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Usage
    template_name = "cube/release_bom.html"
    paginate_by = 50
    search_fields = ("version__purl",)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        release = Release.objects.get(pk=self.kwargs["release_pk"])
        context["release"] = release
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        release_id = self.kwargs["release_pk"]
        queryset = queryset.filter(release=release_id).order_by("project", "scope")
        return queryset


class ReleaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Release
    fields = ["product", "release_number", "commit", "ship_status"]
