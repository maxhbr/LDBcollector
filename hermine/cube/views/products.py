# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from cube.models import Product, Release, Category
from cube.views.mixins import SearchMixin


class ProductListView(
    LoginRequiredMixin, PermissionRequiredMixin, SearchMixin, generic.ListView
):
    permission_required = "cube.view_product"
    model = Product
    template_name = "cube/product_list.html"
    search_fields = ("name", "description")
    paginate_by = 10


class ProductDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView
):
    permission_required = "cube.view_product"
    model = Product
    template_name = "cube/product_detail.html"


class ProductCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView
):
    permission_required = "cube.add_product"
    fields = "__all__"
    model = Product
    template_name = "cube/product_create.html"


class ProductUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView
):
    permission_required = "cube.change_product"
    fields = "__all__"
    model = Product
    template_name = "cube/product_update.html"


class ProductDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView
):
    permission_required = "cube.delete_product"
    model = Product
    success_url = reverse_lazy("cube:product_list")


class ReleaseCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView
):
    permission_required = "cube.add_release"
    fields = ["release_number"]
    model = Release
    template_name = "cube/release_create.html"
    product = None

    def form_valid(self, form):
        form.instance.product = self.product
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, id=self.kwargs["product_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = self.product
        return context


class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = "cube.view_category"
    model = Category


class CategoryDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView
):
    permission_required = "cube.view_category"
    model = Category


class CategoryCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView
):
    permission_required = "cube.add_category"
    fields = "__all__"
    model = Category
    template_name = "cube/category_create.html"


class CategoryUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView
):
    permission_required = "cube.change_category"
    fields = "__all__"
    model = Category
    template_name = "cube/category_update.html"
