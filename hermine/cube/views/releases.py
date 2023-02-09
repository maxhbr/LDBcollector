# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
import csv
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.views import generic
from django.views.generic import (
    UpdateView,
    DetailView,
    TemplateView,
)

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
    get_generic_usages,
)
from cube.views.mixins import SearchMixin, ReleaseContextMixin

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
                You can add components from another source or check the
                validation steps you need to achieve in the <b><a
                href="{reverse("cube:release_validation",
                kwargs={"pk": self.object.id})}"> Validation tab</a></b>.
                """
            ),
        )

        return super().form_valid(form)


class ReleaseObligView(LoginRequiredMixin, generic.DetailView):
    """
    Lists relevant obligations for a given release
    """

    model = Release
    template_name = "cube/release_oblig.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usages = self.object.usage_set.all()
        (
            generics_involved,
            orphaned_licenses,
            licenses_involved,
        ) = get_usages_obligations(usages)
        context["generics_involved"] = generics_involved
        context["orphaned_licenses"] = orphaned_licenses
        context["licenses_involved"] = licenses_involved
        return context


class ReleaseGenericView(LoginRequiredMixin, ReleaseContextMixin, TemplateView):
    template_name = "cube/release_generic.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        release_usages = Usage.objects.filter(
            release__id=self.kwargs["release_pk"],
            licenses_chosen__obligation__generic__id=self.kwargs["generic_id"],
        )
        generic = get_object_or_404(Generic, pk=self.kwargs["generic_id"])
        triggering_usages = get_generic_usages(release_usages, generic)
        context["usages"] = triggering_usages
        context["generic"] = generic
        return context


class ReleaseSummaryView(LoginRequiredMixin, ReleaseContextMixin, generic.ListView):
    model = Exploitation
    template_name = "cube/release_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scopes_in_release = (
            self.release.usage_set.values("project", "scope")
            .annotate(count=Count("*"))
            .values("project", "scope", "count")
            .order_by("project", "scope")
        )
        exploitations = self.get_queryset().values(
            "project", "scope", "exploitation", "id"
        )
        explicit_exploitations = dict()
        for key, value in Exploitation._meta.get_field("exploitation").choices:
            explicit_exploitations[key] = value

        full_exploitations = dict()
        for scope_in_release in scopes_in_release:
            full_scope = scope_in_release["project"] + scope_in_release["scope"]
            full_exploitations[full_scope] = dict()
            full_exploitations[full_scope]["scope"] = scope_in_release["scope"]
            full_exploitations[full_scope]["project"] = scope_in_release["project"]
            full_exploitations[full_scope]["count"] = scope_in_release["count"]
        for exploitation in exploitations:
            full_scope = exploitation["project"] + exploitation["scope"]
            print("exploitation,", full_scope)
            if full_scope in full_exploitations:
                full_exploitations[full_scope]["exploitation"] = explicit_exploitations[
                    exploitation["exploitation"]
                ]
                full_exploitations[full_scope]["exploitation_id"] = exploitation["id"]
            else:
                full_exploitations[full_scope] = dict()
                full_exploitations[full_scope]["scope"] = exploitation["scope"]
                full_exploitations[full_scope]["project"] = exploitation["project"]
                full_exploitations[full_scope]["exploitation"] = explicit_exploitations[
                    exploitation["exploitation"]
                ]
                full_exploitations[full_scope]["exploitation_id"] = exploitation["id"]

        context["full_exploitations"] = list(full_exploitations.values())
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(release=self.release)
            .order_by("project", "scope")
        )


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


class ReleaseSBOMView(
    LoginRequiredMixin, SearchMixin, ReleaseContextMixin, generic.ListView
):
    model = Usage
    template_name = "cube/release_bom.html"
    paginate_by = 50
    search_fields = ("version__purl",)

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        release_id = self.kwargs["release_pk"]
        queryset = queryset.filter(release=release_id).order_by("project", "scope")
        return queryset


class ReleaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Release
    fields = ["product", "release_number", "commit", "ship_status"]
