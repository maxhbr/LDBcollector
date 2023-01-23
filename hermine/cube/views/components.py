# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import get_object_or_404, redirect

from cube.forms.components import LicenseCurationCreateForm, LicenseCurationUpdateForm
from cube.forms.release_validation import CreateLicenseCurationForm
from cube.models import Component, LicenseCuration, Funding
from cube.views.mixins import SearchMixin, SaveAuthorMixin
from cube.utils.funding import get_fundings_from_purl


class ComponentListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Component
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


class PopularListView(LoginRequiredMixin, generic.ListView):
    model = Component
    template_name = "cube/component_popular.html"

    def get_queryset(self):
        return Component.objects.annotate(
            popularity=Count("versions__usage__id")
        ).order_by("-popularity")[:50]


class ComponentView(LoginRequiredMixin, generic.DetailView):
    template_name = "cube/component.html"
    model = Component


class LicenseCurationListView(LoginRequiredMixin, generic.ListView):
    model = LicenseCuration
    template_name = "cube/licensecuration_list.html"


class LicenseCurationCreateView(
    LoginRequiredMixin, SaveAuthorMixin, generic.CreateView
):
    model = LicenseCuration
    form_class = LicenseCurationCreateForm
    success_url = reverse_lazy("cube:licensecurations")


class LicenseCurationUpdateView(
    LoginRequiredMixin, SaveAuthorMixin, generic.UpdateView
):
    model = LicenseCuration
    form_class = LicenseCurationUpdateForm
    success_url = reverse_lazy("cube:licensecurations")


@login_required
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
