# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django_filters.views import FilterView

from cube.filters import ComponentFilter, LicenseCurationFilter
from cube.forms.components import LicenseCurationCreateForm, LicenseCurationUpdateForm
from cube.models import Component, LicenseCuration, Funding, Version
from cube.utils.funding import get_fundings_from_purl
from cube.views.mixins import SaveAuthorMixin, QuerySuccessUrlMixin


class ComponentListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FilterView,
):
    permission_required = "cube.view_component"
    model = Component
    template_name = "cube/component_list.html"
    paginate_by = 30
    ordering = ["name"]
    filterset_class = ComponentFilter

    def get_queryset(self):
        return Component.objects.annotate(usages_count=Count("versions__usage__id"))


class ComponentDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView
):
    permission_required = "cube.view_component"
    template_name = "cube/component_detail.html"
    model = Component


class ComponentUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView
):
    permission_required = "cube.change_component"
    model = Component
    template_name = "cube/component_update.html"
    fields = [
        "name",
        "purl_type",
        "description",
        "programming_language",
        "spdx_expression",
        "homepage_url",
    ]

    def get_success_url(self):
        return reverse_lazy("cube:component_detail", args=[self.object.id])


class ComponentCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView
):
    permission_required = "cube.add_component"
    model = Component
    template_name = "cube/component_create.html"
    fields = [
        "name",
        "purl_type",
        "description",
        "programming_language",
        "spdx_expression",
        "homepage_url",
    ]

    def get_success_url(self):
        return reverse_lazy("cube:component_detail", args=[self.object.id])


class VersionCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView
):
    permission_required = "cube.add_version"
    model = Version
    template_name = "cube/version_form.html"
    fields = [
        "version_number",
        "purl",
        "declared_license_expr",
        "spdx_valid_license_expr",
        "corrected_license",
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["component"] = get_object_or_404(Component, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        component = get_object_or_404(Component, pk=self.kwargs["pk"])
        form.instance.component = component
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("cube:component_detail", args=[self.kwargs["pk"]])


class VersionUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    QuerySuccessUrlMixin,
    generic.UpdateView,
):
    permission_required = "cube.change_version"
    model = Version
    template_name = "cube/version_form.html"
    fields = [
        "version_number",
        "purl",
        "declared_license_expr",
        "spdx_valid_license_expr",
        "corrected_license",
    ]

    def get_default_success_url(self):
        return reverse_lazy("cube:component_detail", args=[self.object.component.id])


class LicenseCurationListView(LoginRequiredMixin, PermissionRequiredMixin, FilterView):
    permission_required = "cube.view_licensecuration"
    paginate_by = 50
    model = LicenseCuration
    template_name = "cube/licensecuration_list.html"
    filterset_class = LicenseCurationFilter


class LicenseCurationCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, SaveAuthorMixin, generic.CreateView
):
    permission_required = "cube.add_licensecuration"
    model = LicenseCuration
    template_name = "cube/licensecuration_form.html"
    form_class = LicenseCurationCreateForm
    success_url = reverse_lazy("cube:licensecuration_list")


class LicenseCurationUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SaveAuthorMixin,
    QuerySuccessUrlMixin,
    generic.UpdateView,
):
    permission_required = "cube.change_licensecuration"
    model = LicenseCuration
    template_name = "cube/licensecuration_form.html"
    form_class = LicenseCurationUpdateForm
    success_url = reverse_lazy("cube:licensecuration_list")


class LicenseCurationDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView
):
    permission_required = "cube.delete_licensecuration"
    model = LicenseCuration
    template_name = "cube/licensecuration_confirm_delete.html"
    success_url = reverse_lazy("cube:licensecuration_list")


@login_required
@permission_required("cube.change_component")
def component_update_funding(request, component_id):
    component = get_object_or_404(Component, pk=component_id)
    fundings = None
    versions = component.versions.all()
    version = versions[0]
    purl = version.purl
    if purl:
        fundings = get_fundings_from_purl(purl)
    if fundings:
        for funding in fundings:
            new_funding, created = Funding.objects.get_or_create(
                component=component,
                url=funding["url"],
                defaults={"type": funding["type"]},
            )
    return redirect(reverse_lazy("cube:component_detail", args=[component_id]))
