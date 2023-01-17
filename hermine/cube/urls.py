# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.urls import path, include
from rest_framework.authtoken import views as authviews
from rest_framework_nested import routers

import cube.views.release_validation
from . import views, api_views

app_name = "cube"
urlpatterns = [
    path("", views.IndexView.as_view(), name="root"),
    path("about/", views.AboutView.as_view(), name="about"),
    # Product views
    path("products/", views.ProductListView.as_view(), name="products"),
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path(
        "product/<int:product_pk>/add_release/",
        views.ProductAddReleaseView.as_view(),
        name="product_add_release",
    ),
    path("product/add/", views.ProductAddView.as_view(), name="product_add"),
    path(
        "product/edit/<int:pk>/", views.ProductEditView.as_view(), name="product_edit"
    ),
    # Product categories views
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path(
        "category/<int:pk>/", views.CategoryDetailView.as_view(), name="category_detail"
    ),
    path("category/add/", views.CategoryAddView.as_view(), name="category_add"),
    path(
        "category/edit/<int:pk>/",
        views.CategoryEditView.as_view(),
        name="category_edit",
    ),
    # Components views
    path("components/", views.ComponentListView.as_view(), name="components"),
    path("components/popular/", views.PopularListView.as_view(), name="populars"),
    path("component/<int:pk>/", views.ComponentView.as_view(), name="component_detail"),
    path(
        "licensecurations/",
        views.LicenseCurationListView.as_view(),
        name="licensecurations",
    ),
    path(
        "licensecurations/add/",
        views.LicenseCurationCreateView.as_view(),
        name="licensecuration_create",
    ),
    path(
        "licensecurations/update/<int:pk>/",
        views.LicenseCurationUpdateView.as_view(),
        name="licensecuration_update",
    ),
    path(
        "licensecurations/export/",
        views.ExportLicenseCurationsView.as_view(),
        name="licensecurations_export",
    ),
    path(
        "licensecurations/<int:pk>/export/",
        views.ExportSingleLicenseCurationView.as_view(),
        name="licensecuration_export",
    ),
    # Licenses and policy views
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
        "license/<int:pk>/print/",
        views.PrintLicense.as_view(),
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
    path(
        "export/licenses/", views.ExportLicensesView.as_view(), name="export_licenses"
    ),
    path(
        "export/generics/", views.ExportGenericsView.as_view(), name="export_generics"
    ),
    # License policy views
    path(
        "license/<int:license_pk>/add_autorized_context/",
        views.AuthorizedContextCreateView.as_view(),
        name="authorized_context_create",
    ),
    path(
        "authorized_context/<int:pk>/edit/",
        views.AuthorizedContextUpdateView.as_view(),
        name="authorized_context_edit",
    ),
    path(
        "authorized_context/",
        views.AuthorizedContextListView.as_view(),
        name="authorized_context_list",
    ),
    path(
        "derogations/",
        views.DerogationListView.as_view(),
        name="derogations",
    ),
    path(
        "licensechoices/", views.LicenseChoiceListView.as_view(), name="licensechoices"
    ),
    # Releases views
    path(
        "release/<int:pk>/edit/",
        views.ReleaseUpdateView.as_view(),
        name="release_edit",
    ),
    path(
        "release/<int:pk>/",
        views.ReleaseSummaryView.as_view(),
        name="release_summary",
    ),
    path(
        "release/<int:release_pk>/exploitations/",
        views.ReleaseExploitationsListView.as_view(),
        name="release_list_exploitations",
    ),
    path(
        "release/<int:release_pk>/edit_exploitation/<int:pk>/",
        views.ReleaseEditExploitationView.as_view(),
        name="release_edit_exploitation",
    ),
    path(
        "release/<int:release_pk>/add_exploitation/",
        views.ReleaseAddExploitationView.as_view(),
        name="release_add_exploitation",
    ),
    path(
        "release/<int:release_pk>/delete_exploitation/<int:pk>/",
        views.ReleaseDeleteExploitationView.as_view(),
        name="release_delete_exploitation",
    ),
    path(
        "release/<int:pk>/import/",
        views.ReleaseImportView.as_view(),
        name="release_import",
    ),
    path(
        "release/<int:pk>/bom/export/",
        views.ReleaseBomExportView.as_view(),
        name="release_bom_export",
    ),
    path(
        "release/<int:release_pk>/bom/",
        views.ReleaseSBOMView.as_view(),
        name="release_bom",
    ),
    path(
        "release/<int:pk>/obligations/",
        views.ReleaseObligView.as_view(),
        name="release_oblig",
    ),
    path(
        "release/<int:release_pk>/obligations/<int:generic_id>/",
        views.ReleaseGenericView.as_view(),
        name="release_generic",
    ),
    # Release validation related views
    path(
        "release/<int:pk>/validation/",
        views.ReleaseValidationView.as_view(),
        name="release_validation",
    ),
    path(
        "usage/<int:usage_pk>/add_license_curation/",
        views.ReleaseLicenseCurationCreateView.as_view(),
        name="release_licensecuration_create",
    ),
    path(
        "release/<int:id>/validation/fixed_licenses/",
        views.ReleaseCuratedLicensesListView.as_view(),
        name="release_curated_licenses",
    ),
    path(
        "usage/<int:pk>/update_license_curation/",
        views.UpdateLicenseCurationView.as_view(),
        name="release_update_license_curation",
    ),
    path(
        "usage/<int:usage_pk>/add_ands_validation/",
        views.ReleaseAndsValidationCreateView.as_view(),
        name="release_andsvalidation_create",
    ),
    path(
        "release/<int:id>/validation/ands_validations/",
        views.ReleaseAndsValidationListView.as_view(),
        name="release_ands_validations",
    ),
    path(
        "usage/<int:pk>/update_ands_validation/",
        views.UpdateAndsValidationView.as_view(),
        name="release_update_andsvalidation",
    ),
    path(
        "usage/<int:usage_pk>/add_license_choice/",
        views.ReleaseLicenseChoiceCreateView.as_view(),
        name="release_licensechoice_create",
    ),
    path(
        "release/<int:id>/validation/license_choices/",
        views.ReleaseLicenseChoiceListView.as_view(),
        name="release_license_choices",
    ),
    path(
        "release/update_license_choice/<int:pk>/",
        views.UpdateLicenseChoiceView.as_view(),
        name="release_update_license_choice",
    ),
    path(
        "usage/<int:usage_pk>/add_derogation/<int:license_pk>/",
        views.ReleaseDerogationCreateView.as_view(),
        name="release_derogation_create",
    ),
    # TODO move this in API urls
    path(
        "api/usagesflat/",
        api_views.UsageFlatList.as_view(),
        name="api_usagesflat",
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
router.register(r"curations", api_views.LicenseCurationViewSet, basename="curations")
router.register(r"choices", api_views.LicenseChoiceViewSet, basename="choices")
router.register(r"derogations", api_views.DerogationViewSet, basename="derogations")

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
