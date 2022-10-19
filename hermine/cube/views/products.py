# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy

from cube.models import Product, Release
from cube.views.mixins import SearchMixin


class ProductListView(LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = "cube/product_list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nb_products"] = Product.objects.all().count()
        context["nb_releases"] = Release.objects.all().count()
        return context


class ProductDetailView(LoginRequiredMixin, generic.DetailView):
    model = Product
    template_name = "cube/product_detail.html"


class ProductAddView(LoginRequiredMixin, generic.CreateView):
    fields = "__all__"
    model = Product
    # success_url = reverse_lazy("cube:products")


class ProductListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    model = Product
    template_name = "cube/product_list.html"
    search_fields = ("name", "description")
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nb_products"] = Product.objects.all().count()
        context["nb_releases"] = Release.objects.all().count()
        return context
