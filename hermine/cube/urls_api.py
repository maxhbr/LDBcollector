# SPDX-FileCopyrightText: 2024 Hermine-team
# SPDX-License-Identifier: AGPL-3.0-only
# API urls
from django.urls import path, include
from rest_framework.authtoken import views as authviews
from rest_framework_nested import routers

from cube import api_views


class Router(routers.DefaultRouter):
    APIRootView = api_views.RootView


app_name = "api"
router = Router()

# Validation pipeline endpoints
router.register(r"upload_spdx", api_views.UploadSPDXViewSet, basename="upload_spdx")
router.register(
    r"upload_cyclonedx", api_views.UploadCYCLONEDXViewSet, basename="upload_cyclonedx"
)
router.register(r"upload_ort", api_views.UploadORTViewSet, basename="upload_ort")
router.register(r"releases", api_views.ReleaseViewSet, basename="releases")

# Compliance actions
router.register(r"generics", api_views.GenericViewSet, basename="generics")

# Models CRUD viewsets
router.register(r"obligations", api_views.ObligationViewSet, basename="obligations")
router.register(r"components", api_views.ComponentViewSet, basename="components")
router.register(r"versions", api_views.VersionViewSet, basename="versions")
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

component_router = routers.NestedSimpleRouter(router, r"components", lookup="component")
component_router.register(
    r"versions", api_views.VersionViewSet, basename="component-versions"
)

urlpatterns = router.urls
urlpatterns += [
    path("", include(obligation_router.urls)),
    path("", include(product_router.urls)),
    path("", include(release_router.urls)),
    path("", include(component_router.urls)),
    path("token-auth/", authviews.obtain_auth_token),
]
