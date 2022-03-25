# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views import generic

from cube.models import Component


class ComponentList(LoginRequiredMixin, generic.ListView):
    model = Component
    paginate_by = 30
    ordering = ["name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        populars = Component.objects.annotate(
            popularity=Count("version__usage__id")
        ).order_by("-popularity")[:10]
        context["populars"] = populars
        return context


class ComponentView(LoginRequiredMixin, generic.DetailView):
    template_name = "cube/component.html"
    model = Component

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
