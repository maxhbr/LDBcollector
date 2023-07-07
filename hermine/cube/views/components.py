# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import get_object_or_404, redirect

from cube.forms.components import LicenseCurationCreateForm, LicenseCurationUpdateForm
from cube.models import Component, LicenseCuration, Funding
from cube.views.mixins import SearchMixin, SaveAuthorMixin
from cube.utils.funding import get_fundings_from_purl


class ComponentListView(
    LoginRequiredMixin, PermissionRequiredMixin, SearchMixin, generic.ListView
):
    permission_required = "cube.view_component"
    model = Component
    template_name = "cube/component_list.html"
    paginate_by = 30
    ordering = ["name"]
    search_fields = ("name", "description", "spdx_expression")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        populars = Component.objects.annotate(
            popularity=Count("versions__usage__id")
        ).order_by("-popularity")[:10]
        context["populars"] = populars
        return context


class PopularListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = "cube.view_component"
    model = Component
    template_name = "cube/component_popular.html"

    def get_queryset(self):
        return Component.objects.annotate(
            popularity=Count("versions__usage__id")
        ).order_by("-popularity")[:50]


class ComponentDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView
):
    permission_required = "cube.view_component"
    template_name = "cube/component.html"
    model = Component


class ComponentUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView
):
    permission_required = "cube.change_component"
    model = Component
    template_name = "cube/component_update.html"
    fields = [
        "name",
        "package_repo",
        "description",
        "programming_language",
        "spdx_expression",
        "homepage_url",
    ]

    def get_success_url(self):
        return reverse_lazy("cube:component_detail", args=[self.object.id])


class LicenseCurationListView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.ListView
):
    permission_required = "cube.view_licensecuration"
    model = LicenseCuration
    template_name = "cube/licensecuration_list.html"


class LicenseCurationCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, SaveAuthorMixin, generic.CreateView
):
    permission_required = "cube.add_licensecuration"
    model = LicenseCuration
    template_name = "cube/licensecuration_form.html"
    form_class = LicenseCurationCreateForm
    success_url = reverse_lazy("cube:licensecurations")


class LicenseCurationUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, SaveAuthorMixin, generic.UpdateView
):
    permission_required = "cube.change_licensecuration"
    model = LicenseCuration
    template_name = "cube/licensecuration_form.html"
    form_class = LicenseCurationUpdateForm
    success_url = reverse_lazy("cube:licensecurations")


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
