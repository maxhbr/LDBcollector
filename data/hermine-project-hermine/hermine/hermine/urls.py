# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

"""hermine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.db import connection, Error as DBError
from django.http import HttpResponse, HttpResponseServerError
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Hermine API",
        default_version="v1",
        description="Hermine Rest API documentation",
        # terms_of_service="https://hermine-foss.org/",
        contact=openapi.Contact(email="hermine@inno3.fr"),
        license=openapi.License(name="AGPL-3.0-only"),
    ),
    public=False,
    permission_classes=[
        permissions.IsAuthenticated,
    ],
)


def ready(r):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row is None:
                return HttpResponseServerError("Database: invalid response")
    except DBError:
        return HttpResponseServerError("Database: cannot connect")

    return HttpResponse("OK")


urlpatterns = [
    path("", include("cube.urls")),
    path("ping/", lambda r: HttpResponse("OK")),
    path("ready/", ready),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("oauth/", include("social_django.urls", namespace="social")),
    re_path(
        r"^api-doc(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^api-doc-swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^api-doc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]

if settings.ENABLE_PROFILING:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
