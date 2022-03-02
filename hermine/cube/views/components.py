# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from cube.models import Component


class ComponentList(LoginRequiredMixin, generic.ListView):
    model = Component
    paginate_by = 30
    ordering = ["name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        raw_query = """SELECT cube_component.id,cube_component.name, count(*) AS popularity
        FROM cube_component
        LEFT JOIN cube_version ON cube_version.component_id =cube_component.id
        LEFT JOIN cube_usage ON cube_usage.version_id = cube_version.id
        GROUP BY cube_component.id
        ORDER BY popularity DESC LIMIT 10"""
        populars = Component.objects.raw(raw_query)
        context["populars"] = populars
        return context


class ComponentView(LoginRequiredMixin, generic.DetailView):
    template_name = "cube/component.html"
    model = Component

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
