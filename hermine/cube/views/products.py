# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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


class ProductAddView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    permission_required = "cube.add_product"
    fields = "__all__"
    model = Product
    template_name = "cube/product_add.html"
    # success_url = reverse_lazy("cube:products")


class ProductEditView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    permission_required = "cube.change_product"
    fields = "__all__"
    model = Product
    template_name = "cube/product_edit.html"
    # success_url = reverse_lazy("cube:products")


class ProductAddReleaseView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView
):
    permission_required = "cube.add_release"
    fields = ["product", "release_number"]
    model = Release
    template_name = "cube/product_add_release.html"

    # success_url = reverse_lazy("cube:products")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = Product.objects.get(id=self.kwargs["product_pk"])
        return context


class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = "cube.view_category"
    model = Category


class CategoryDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView
):
    permission_required = "cube.view_category"
    model = Category


class CategoryAddView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    permission_required = "cube.add_category"
    fields = "__all__"
    model = Category
    template_name = "cube/category_add.html"


class CategoryEditView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    permission_required = "cube.change_category"
    fields = "__all__"
    model = Category
    template_name = "cube/category_edit.html"
