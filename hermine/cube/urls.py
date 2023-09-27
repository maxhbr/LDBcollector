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
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("about/", views.AboutView.as_view(), name="about"),
    # Product views
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path(
        "products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    path(
        "products/<int:product_pk>/new_release/",
        views.ReleaseCreateView.as_view(),
        name="release_create",
    ),
    path("products/new/", views.ProductCreateView.as_view(), name="product_create"),
    path(
        "products/<int:pk>/edit/",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "products/<int:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
    # Product categories views
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path(
        "categories/<int:pk>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path(
        "categories/<int:pk>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category_update",
    ),
    # Components views
    path("components/", views.ComponentListView.as_view(), name="component_list"),
    path(
        "components/popular/",
        views.ComponentPopularListView.as_view(),
        name="component_populars",
    ),
    path(
        "components/<int:pk>/",
        views.ComponentDetailView.as_view(),
        name="component_detail",
    ),
    path(
        "components/<int:pk>/edit/",
        views.ComponentUpdateView.as_view(),
        name="component_update",
    ),
    path(
        "components/<int:pk>/update_funding/",
        views.component_update_funding,
        name="component_update_funding",
    ),
    path(
        "curations/",
        views.LicenseCurationListView.as_view(),
        name="licensecuration_list",
    ),
    path(
        "curations/new/",
        views.LicenseCurationCreateView.as_view(),
        name="licensecuration_create",
    ),
    path(
        "curations/edit/<int:pk>/",
        views.LicenseCurationUpdateView.as_view(),
        name="licensecuration_update",
    ),
    path(
        "curations/export/",
        views.LicenseCurationExportView.as_view(),
        name="licensecuration_export",
    ),
    path(
        "curations/<int:pk>/export/",
        views.LicenseCurationSingleExportView.as_view(),
        name="licensecuration_single_export",
    ),
    # Licenses and policy views
    path("licenses/", views.LicensesListView.as_view(), name="license_list"),
    path(
        "licenses/<int:pk>/", views.LicenseDetailView.as_view(), name="license_detail"
    ),
    path(
        "licenses/<int:pk>/edit/",
        views.LicenseUpdateView.as_view(),
        name="license_update",
    ),
    path("licenses/new/", views.LicenseCreateView.as_view(), name="license_create"),
    path(
        "licenses/<int:pk>/diff/", views.LicenseDiffView.as_view(), name="license_diff"
    ),
    path(
        "licenses/<int:pk>/diff_update/<str:field>/",
        views.LicenseDiffUpdateView.as_view(),
        name="license_diff_update",
    ),
    path("licenses/export/", views.LicenseExportView.as_view(), name="license_export"),
    path(
        "licenses/<int:license_id>/export/",
        views.LicenseSingleExportView.as_view(),
        name="license_export_single",
    ),
    path(
        "licenses/<int:pk>/print/",
        views.LicensePrintView.as_view(),
        name="license_print",
    ),
    path(
        "license/<int:license_pk>/new_obligation/",
        views.ObligationCreateView.as_view(),
        name="obligation_create",
    ),
    path(
        "obligations/<int:pk>/edit/",
        views.ObligationUpdateView.as_view(),
        name="obligation_update",
    ),
    path(
        "obligations/<int:pk>/delete/",
        views.ObligationDeleteView.as_view(),
        name="obligation_delete",
    ),
    path(
        "obligations/<int:pk>/diff_update/<str:field>/",
        views.ObligationDiffUpdateView.as_view(),
        name="obligation_diff_update",
    ),
    path("generics/", views.GenericListView.as_view(), name="generic_list"),
    path(
        "generics/<int:pk>/", views.GenericDetailView.as_view(), name="generic_detail"
    ),
    path("generics/new/", views.GenericCreateView.as_view(), name="generic_create"),
    path(
        "generics/<int:pk>/edit/",
        views.GenericUpdateView.as_view(),
        name="generic_update",
    ),
    path(
        "generics/<int:pk>/diff/", views.GenericDiffView.as_view(), name="generic_diff"
    ),
    path(
        "generics/<int:pk>/diff_update/<str:field>/",
        views.GenericDiffUpdateView.as_view(),
        name="generic_diff_update",
    ),
    path("generics/export/", views.GenericExportView.as_view(), name="generic_export"),
    # License policy views
    path(
        "authorized_contexts/",
        views.AuthorizedContextListView.as_view(),
        name="authorizedcontext_list",
    ),
    path(
        "licenses/<int:license_pk>/new_autorized_context/",
        views.AuthorizedContextCreateView.as_view(),
        name="authorizedcontext_create",
    ),
    path(
        "authorized_contexts/<int:pk>/edit/",
        views.AuthorizedContextUpdateView.as_view(),
        name="authorizedcontext_update",
    ),
    path(
        "derogations/",
        views.DerogationListView.as_view(),
        name="derogation_list",
    ),
    path(
        "licensechoices/",
        views.LicenseChoiceListView.as_view(),
        name="licensechoice_list",
    ),
    path(
        "licensechoices/<int:pk>/edit/",
        views.LicenseChoiceUpdateView.as_view(),
        name="licensechoice_update",
    ),
    path(
        "licensechoices/new/",
        views.LicenseChoiceCreateView.as_view(),
        name="licensechoice_create",
    ),
    path("shared/", views.SharedReferenceView.as_view(), name="shared_reference"),
    # Releases views
    path(
        "releases/<int:pk>/edit/",
        views.ReleaseUpdateView.as_view(),
        name="release_update",
    ),
    path(
        "releases/<int:release_pk>/",
        views.ReleaseSummaryView.as_view(),
        name="release_summary",
    ),
    path(
        "releases/<int:pk>/import/",
        views.ReleaseImportView.as_view(),
        name="release_import",
    ),
    path(
        "releases/<int:release_pk>/bom/",
        views.ReleaseBomView.as_view(),
        name="release_bom",
    ),
    path(
        "releases/<int:pk>/bom/export/",
        views.ReleaseBomExportView.as_view(),
        name="release_bom_export",
    ),
    path(
        "releases/<int:pk>/obligations/",
        views.ReleaseObligationsView.as_view(),
        name="release_obligations",
    ),
    path(
        "releases/<int:release_pk>/obligations/<int:generic_id>/",
        views.ReleaseGenericView.as_view(),
        name="release_generic",
    ),
    # Usage views
    path(
        "releases/<int:release_pk>/new_usage/",
        views.UsageCreateView.as_view(),
        name="usage_create",
    ),
    path(
        "usages/<int:pk>/edit/",
        views.UsageUpdateView.as_view(),
        name="usage_update",
    ),
    path(
        "usages/<int:pk>/delete/",
        views.UsageDeleteView.as_view(),
        name="usage_delete",
    ),
    # Release validation related views
    path(
        "releases/<int:pk>/validation/",
        views.ReleaseValidationView.as_view(),
        name="release_validation",
    ),
    ## Step 1
    path(
        "usages/<int:usage_pk>/new_license_curation/",
        views.ReleaseLicenseCurationCreateView.as_view(),
        name="release_licensecuration_create",
    ),
    path(
        "release/<int:id>/validation/fixed_licenses/",
        views.ReleaseCuratedLicensesView.as_view(),
        name="release_curated_licenses",
    ),
    path(
        "usages/<int:pk>/update_license_curation/",
        views.UpdateLicenseCurationView.as_view(),
        name="release_update_license_curation",
    ),
    ### Step 2
    path(
        "usages/<int:usage_pk>/new_ands_validation/",
        views.ReleaseAndsValidationCreateView.as_view(),
        name="release_andsvalidation_create",
    ),
    path(
        "releases/<int:id>/validation/ands_validations/",
        views.ReleaseAndsConfirmationView.as_view(),
        name="release_ands_validations",
    ),
    path(
        "usages/<int:pk>/update_ands_validation/",
        views.ReleaseUpdateAndsValidationView.as_view(),
        name="release_update_andsvalidation",
    ),
    ### Step 3
    path(
        "releases/<int:release_pk>/exploitations/new/",
        views.ReleaseExploitationCreateView.as_view(),
        name="release_exploitation_create",
    ),
    path(
        "releases/<int:release_pk>/exploitations/<int:pk>/edit/",
        views.ReleaseExploitationUpdateView.as_view(),
        name="release_exploitation_update",
    ),
    path(
        "release/<int:release_pk>/exploitations/<int:pk>/delete/",
        views.ReleaseExploitationDeleteView.as_view(),
        name="release_delete_exploitation",
    ),
    ## Step 4
    path(
        "usage/<int:usage_pk>/add_license_choice/",
        views.ReleaseLicenseChoiceCreateView.as_view(),
        name="release_licensechoice_create",
    ),
    path(
        "release/<int:release_pk>/validation/license_choices/",
        views.ReleaseLicenseChoiceListView.as_view(),
        name="release_licensechoice_list",
    ),
    path(
        "release/update_license_choice/<int:pk>/",
        views.ReleaseUpdateLicenseChoiceView.as_view(),
        name="release_update_license_choice",
    ),
    ## Step 5
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
