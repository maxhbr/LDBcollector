# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib import admin

# Register your models here.

from .models import Product
from .models import Category
from .models import Release
from .models import Component
from .models import Version
from .models import Usage
from .models import License
from .models import Generic
from .models import Obligation
from .models import Derogation
from .models import LicenseChoice
from .models import Exploitation


class ObligationInline(admin.StackedInline):
    model = Obligation
    extra = 1


class ObligationInlineTab(admin.TabularInline):
    model = Obligation
    extra = 1


class ObligationAdmin(admin.ModelAdmin):
    search_fields = ["name", "license__spdx_id"]


class VersionInlineTab(admin.TabularInline):
    model = Version
    extra = 1


class UsageInlineTab(admin.TabularInline):
    model = Usage
    extra = 1


class LicenseAdmin(admin.ModelAdmin):
    inlines = [ObligationInline]
    list_display = ("spdx_id", "color", "status")
    list_filter = ["status"]
    search_fields = ["spdx_id"]


class GenericAdmin(admin.ModelAdmin):
    inlines = [ObligationInlineTab]
    list_display = ("name", "in_core", "metacategory", "team")
    list_filter = ["in_core"]
    ordering = ["in_core"]


class ComponentAdmin(admin.ModelAdmin):
    inlines = [VersionInlineTab]
    search_fields = ["name", "description"]


class ReleaseAdmin(admin.ModelAdmin):
    inlines = [UsageInlineTab]


class UsageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "version")
    search_fields = [
        "release__product__name",
        "version__component__name",
        "licenses_chosen__spdx_id",
        "pk",
        "status",
    ]


class VersionAdmin(admin.ModelAdmin):
    search_fields = ["purl"]


admin.site.register(License, LicenseAdmin)
admin.site.register(Obligation, ObligationAdmin)

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Generic, GenericAdmin)
admin.site.register(Derogation)
admin.site.register(LicenseChoice)
admin.site.register(Exploitation)
