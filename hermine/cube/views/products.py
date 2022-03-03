# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from cube.models import Product, Release


class ProductListView(LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = "cube/product_list.html"
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nb_products"] = Product.objects.all().count()
        context["nb_releases"] = Release.objects.all().count()
        return context
