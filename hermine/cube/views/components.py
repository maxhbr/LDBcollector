# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from cube.models import Component


class ComponentList(LoginRequiredMixin, generic.ListView):
    model = Component
    paginate_by = 50
    ordering = ["name"]


class ComponentView(LoginRequiredMixin, generic.DetailView):
    template_name = "cube/component.html"
    model = Component

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
