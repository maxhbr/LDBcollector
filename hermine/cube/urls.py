# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.conf.urls import include
from django.urls import path
from rest_framework_nested import routers
from rest_framework.authtoken import views as authviews

from . import views, api_views, f_views

app_name = "cube"
urlpatterns = [
    path("", f_views.index, name="racine"),
    path("license/<int:license_id>", f_views.license, name="license"),
    path(
        "license/<int:license_id>/export/",
        f_views.export_specific_license,
        name="export_license",
    ),
    path(
        "license/<int:license_id>/print/",
        f_views.print_license,
        name="print_license",
    ),
    path("generics", f_views.generics, name="generics"),
    path("generic/<int:generic_id>", f_views.generic, name="generic"),
    path("export/licenses", f_views.export_licenses, name="export_licenses"),
    path("export/generics", f_views.export_generics, name="export_generics"),
    path("import/generics", f_views.upload_generics_file, name="import_generics"),
    path("import/licenses", f_views.upload_licenses_file, name="import_licenses"),
    path("import/bom", f_views.import_bom, name="import_bom"),
    path("products", views.ProductListView.as_view(), name="products"),
    path("release/<int:pk>", views.ReleaseView.as_view(), name="release_synthesis"),
    path("release/<int:pk>/bom", views.ReleaseBomView.as_view(), name="bom"),
    path("release/<int:pk>/obligations", views.ReleaseObligView.as_view(), name="oblig"),
    path(
        "release/<int:release_id>/obligations/<int:generic_id>",
        f_views.release_generic,
        name="release_generic",
    ),
    path(
        "release/<int:release_id>/derogation/<int:usage_id>/",
        f_views.release_add_derogation,
        name="release_add_derogation",
    ),
    path(
        "release/<int:release_id>/send_derogation/<int:usage_id>/",
        f_views.release_send_derogation,
        name="release_send_derogation",
    ),
    path(
        "release/<int:release_id>/choice/<int:usage_id>/",
        f_views.release_add_choice,
        name="release_add_choice",
    ),
    path(
        "release/<int:release_id>/send_choice/<int:usage_id>/",
        f_views.release_send_choice,
        name="release_send_choice",
    ),
    path(
        "release/<int:release_id>/exploitation",
        f_views.release_exploitation,
        name="release_exploitation",
    ),
    path(
        "release/<int:release_id>/send_exploitation",
        f_views.release_send_exploitation,
        name="release_send_exploitation",
    ),
    path("licenses/<int:page>/", f_views.licenses, name="licenses"),
    path("component/<int:pk>", views.ComponentView.as_view(), name="component"),
    path("components", views.ComponentList.as_view(), name="components"),
    path(
        "propagate_choices/<int:release_id>",
        f_views.propagate_choices,
        name="propagate_choices",
    ),
    path("about", f_views.about, name="about"),
    path("api/token-auth/", authviews.obtain_auth_token),
]

router = routers.SimpleRouter()

router.register(r"api", api_views.RootViewSet, basename="api_root")
router.register(r"api/generics", api_views.GenericViewSet, basename="generic")
router.register(r"api/releases", api_views.ReleaseViewSet, basename="release")
router.register(r"api/upload_spdx", api_views.UploadSPDXViewSet, basename="upload_spdx")
router.register(r"api/upload_ort", api_views.UploadORTViewSet, basename="upload_ort")



release_router = routers.NestedSimpleRouter(router, r"api/releases")
release_router.register(
    r"validation-1", api_views.UnnormalisedUsagesViewSet, basename="validation-1"
)
release_router.register(
    r"validation-2", api_views.LicensesToCheckViewSet, basename="validation-2"
)
release_router.register(
    r"validation-3", api_views.LicensesUsagesViewSet, basename="validation-3"
)
release_router.register(
    r"validation-4", api_views.LicensesAgainstPolicyViewSet, basename="validation-4"
)

router.register(r"api/obligations", api_views.ObligationViewSet, basename="obligation")
router.register(r"api/components", api_views.ComponentViewSet, basename="component")
router.register(r"api/versions", api_views.VersionViewSet, basename="component")
router.register(r"api/usages", api_views.UsageViewSet, basename="release_exploit")
router.register(r"api/products", api_views.ProductViewSet, basename="product")

router.register(r"api/licenses", api_views.LicenseViewSet, basename="license")

obligation_router = routers.NestedSimpleRouter(router, r"api/licenses")
obligation_router.register(
    r"obligations", api_views.ObligationViewSet, basename="license-obligations"
)

product_router = routers.NestedSimpleRouter(router, r"api/products")
product_router.register(
    r"releases", api_views.ReleaseViewSet, basename="product-releases"
)

version_router = routers.NestedSimpleRouter(router, r"api/components")
version_router.register(
    r"versions", api_views.VersionViewSet, basename="component-versions"
)

urlpatterns += router.urls
urlpatterns += obligation_router.urls
urlpatterns += product_router.urls
urlpatterns += version_router.urls
urlpatterns += release_router.urls
