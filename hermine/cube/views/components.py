# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views import generic

from cube.forms.components import LicenseCurationCreateForm, LicenseCurationUpdateForm
from cube.forms.release_validation import CreateLicenseCurationForm
from cube.models import Component, LicenseCuration
from cube.views.mixins import SearchMixin, SaveAuthorMixin


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
        ).order_by("-popularity")[:10]


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
