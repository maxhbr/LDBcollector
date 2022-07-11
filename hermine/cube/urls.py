# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.urls import path, include
from rest_framework.authtoken import views as authviews
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import views, api_views

app_name = "cube"
urlpatterns = [
    path("", views.IndexView.as_view(), name="root"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("products/", views.ProductListView.as_view(), name="products"),
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("components/", views.ComponentList.as_view(), name="components"),
    path("component/<int:pk>/", views.ComponentView.as_view(), name="component_detail"),
    path("license/<int:license_id>/", views.license, name="license"),
    path(
        "license/<int:license_id>/export/",
        views.export_specific_license,
        name="export_license",
    ),
    path(
        "license/<int:license_id>/print/",
        views.print_license,
        name="print_license",
    ),
    path("generics/", views.generics, name="generics"),
    path("generic/<int:generic_id>/", views.generic, name="generic"),
    path("export/licenses/", views.export_licenses, name="export_licenses"),
    path("export/generics/", views.export_generics, name="export_generics"),
    path("import/generics/", views.upload_generics_file, name="import_generics"),
    path("import/licenses/", views.upload_licenses_file, name="import_licenses"),
    path("release/<int:pk>/", views.ReleaseView.as_view(), name="release_detail"),
    path("release/<int:pk>/bom/", views.ReleaseBomView.as_view(), name="release_bom"),
    path(
        "release/<int:pk>/obligations/", views.ReleaseObligView.as_view(), name="oblig"
    ),
    path(
        "release/<int:release_id>/obligations/<int:generic_id>/",
        views.release_generic,
        name="release_generic",
    ),
    path(
        "release/<int:release_id>/derogation/<int:usage_id>/",
        views.release_add_derogation,
        name="release_add_derogation",
    ),
    path(
        "release/<int:release_id>/send_derogation/<int:usage_id>/",
        views.release_send_derogation,
        name="release_send_derogation",
    ),
    path(
        "release/<int:release_id>/choice/<int:usage_id>/",
        views.release_add_choice,
        name="release_add_choice",
    ),
    path(
        "release/<int:release_id>/send_choice/<int:usage_id>/",
        views.release_send_choice,
        name="release_send_choice",
    ),
    path(
        "release/<int:pk>/exploitation/",
        views.ReleaseExploitationView.as_view(),
        name="release_exploitation",
    ),
    path("licenses/<int:page>/", views.licenses, name="licenses"),
    path("api/token-auth/", authviews.obtain_auth_token),
]

# API urls


class Router(routers.DefaultRouter):
    APIRootView = api_views.RootView


router = Router()

# Validation pipeline endpoints
router.register(r"upload_spdx", api_views.UploadSPDXViewSet, basename="upload_spdx")
router.register(r"upload_ort", api_views.UploadORTViewSet, basename="upload_ort")
router.register(r"releases", api_views.ReleaseViewSet, basename="release")

# Generic obligations
router.register(r"generics", api_views.GenericViewSet, basename="generic")


# Models CRUD viewsets
router.register(r"obligations", api_views.ObligationViewSet, basename="obligation")
router.register(r"components", api_views.ComponentViewSet, basename="component")
router.register(r"usages", api_views.UsageViewSet, basename="release_exploit")
router.register(r"products", api_views.ProductViewSet, basename="product")
router.register(r"licenses", api_views.LicenseViewSet, basename="license")
router.register(r"choices", api_views.LicenseChoiceViewSet, basename="choices")

obligation_router = routers.NestedSimpleRouter(router, r"licenses")
obligation_router.register(
    r"obligations", api_views.ObligationViewSet, basename="license-obligations"
)

product_router = routers.NestedSimpleRouter(router, r"products")
product_router.register(
    r"releases", api_views.ReleaseViewSet, basename="product-releases"
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
            + version_router.urls,
        ),
    ),
)
