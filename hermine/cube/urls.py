# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.urls import path, include
from rest_framework.authtoken import views as authviews
from rest_framework_nested import routers

from . import views, api_views

app_name = "cube"
urlpatterns = [
    path("", views.IndexView.as_view(), name="root"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("products/", views.ProductListView.as_view(), name="products"),
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("product/add/", views.ProductAddView.as_view(), name="product_add"),
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path(
        "category/<int:pk>/", views.CategoryDetailView.as_view(), name="category_detail"
    ),
    path("components/", views.ComponentListView.as_view(), name="components"),
    path("components/popular/", views.PopularListView.as_view(), name="populars"),
    path("component/<int:pk>/", views.ComponentView.as_view(), name="component_detail"),
    path(
        "licensecurations/",
        views.LicenseCurationListView.as_view(),
        name="licensecurations",
    ),
    path(
        "licensecurations/update/<int:pk>/",
        views.LicenseCurationUpdateView.as_view(),
        name="licensecuration_update",
    ),
    path("licenses/", views.LicensesListView.as_view(), name="licenses"),
    path("license/<int:pk>/", views.LicenseDetailView.as_view(), name="license"),
    path(
        "license/<int:pk>/edit/", views.LicenseUpdateView.as_view(), name="license_edit"
    ),
    path(
        "license/<int:license_id>/export/",
        views.Export1LicenseView.as_view(),
        name="export_license",
    ),
    path(
        "license/<int:license_id>/print/",
        views.print_license,
        name="print_license",
    ),
    path(
        "license/<int:license_pk>/add_obligation/",
        views.ObligationCreateView.as_view(),
        name="obligation_create",
    ),
    path(
        "obligation/<int:pk>/edit/",
        views.ObligationUpdateView.as_view(),
        name="obligation_edit",
    ),
    path(
        "obligation/<int:pk>/delete/",
        views.ObligationDeleteView.as_view(),
        name="obligation_delete",
    ),
    path("generics/", views.GenericListView.as_view(), name="generics"),
    path("generic/<int:pk>/", views.GenericDetailView.as_view(), name="generic"),
    path("derogations/", views.DerogationListView.as_view(), name="derogations"),
    path(
        "export/licenses/", views.ExportLicensesView.as_view(), name="export_licenses"
    ),
    path(
        "export/generics/", views.ExportGenericsView.as_view(), name="export_generics"
    ),
    path(
        "release/<int:pk>/validation/",
        views.ReleaseView.as_view(),
        name="release_validation",
    ),
    path(
        "release/<int:id>/validation/fixed_licenses/",
        views.ReleaseFixedLicensesList.as_view(),
        name="release_normalized_usages",
    ),
    path(
        "release/<int:pk>/",
        views.ReleaseSummaryView.as_view(),
        name="release_summary",
    ),
    path("release/<int:pk>/bom/", views.ReleaseBomView.as_view(), name="release_bom"),
    path(
        "release/<int:pk>/bom/export/",
        views.ReleaseBomExportView.as_view(),
        name="release_bom_export",
    ),
    path(
        "release/<int:pk>/obligations/", views.ReleaseObligView.as_view(), name="oblig"
    ),
    path(
        "release/<int:release_id>/obligations/<int:generic_id>/",
        views.release_generic,
        name="release_generic",
    ),
    path(
        "release/update_license_choice/<int:pk>/",
        views.UpdateLicenseChoiceView.as_view(),
        name="usage_update_license_choice",
    ),
    path(
        "usage/<int:usage_pk>/add_derogation/<int:license_pk>/",
        views.CreateDerogationView.as_view(),
        name="add_derogation",
    ),
    path(
        "usage/<int:usage_pk>/add_license_curation/",
        views.CreateLicenseCurationView.as_view(),
        name="licensecuration_create",
    ),
    path(
        "usage/<int:usage_pk>/add_expression_validation/",
        views.CreateExpressionValidationView.as_view(),
        name="expressionvalidation_create",
    ),
    path(
        "usage/<int:usage_pk>/add_license_choice/",
        views.CreateLicenseChoiceView.as_view(),
        name="licensechoice_create",
    ),
    path("api/token-auth/", authviews.obtain_auth_token),
]

# API urls


class Router(routers.DefaultRouter):
    APIRootView = api_views.RootView


router = Router()

# Validation pipeline endpoints
router.register(r"upload_spdx", api_views.UploadSPDXViewSet, basename="upload_spdx")
router.register(r"upload_ort", api_views.UploadORTViewSet, basename="upload_ort")
router.register(r"releases", api_views.ReleaseViewSet, basename="releases")

# Generic obligations
router.register(r"generics", api_views.GenericViewSet, basename="generics")


# Models CRUD viewsets
router.register(r"obligations", api_views.ObligationViewSet, basename="obligations")
router.register(r"components", api_views.ComponentViewSet, basename="components")
router.register(r"usages", api_views.UsageViewSet, basename="usages")
router.register(r"products", api_views.ProductViewSet, basename="products")
router.register(r"licenses", api_views.LicenseViewSet, basename="licenses")
router.register(r"choices", api_views.LicenseChoiceViewSet, basename="choices")

obligation_router = routers.NestedSimpleRouter(router, r"licenses")
obligation_router.register(
    r"obligations",
    api_views.ObligationViewSet,
    basename="license-obligations",
)

product_router = routers.NestedSimpleRouter(router, r"products")
product_router.register(
    r"releases", api_views.ReleaseViewSet, basename="product-releases"
)

release_router = routers.NestedSimpleRouter(router, r"releases", lookup="release")
release_router.register(
    r"exploitations", api_views.ExploitationViewSet, basename="releases-exploitations"
)

version_router = routers.NestedSimpleRouter(router, r"components")
version_router.register(
    r"versions", api_views.VersionViewSet, basename="component-versions"
)

urlpatterns.append(
    path(
        "api/",
        include(
            router.urls
            + obligation_router.urls
            + product_router.urls
            + release_router.urls
            + version_router.urls,
        ),
    ),
)
