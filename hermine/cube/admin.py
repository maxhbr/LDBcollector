# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django import forms
from django.contrib import admin

# Register your models here.

from .models import Product, ExpressionValidation
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
from .models import Team
from .utils.licenses import is_ambiguous


class ObligationInline(admin.StackedInline):
    model = Obligation
    extra = 1


class ObligationInlineTab(admin.TabularInline):
    model = Obligation
    extra = 1


class ObligationAdmin(admin.ModelAdmin):
    search_fields = ["name", "license__spdx_id"]


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


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
    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "spdx_id",
                    "long_name",
                    "url",
                    "verbatim",
                    "osi_approved",
                    "fsf_approved",
                    "law_choice",
                    "venue_choice",
                )
            },
        ),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": (
                    "license_version",
                    "radical",
                    "autoupgrade",
                    "inspiration_spdx",
                    "inspiration",
                ),
            },
        ),
        (
            "Evaluation",
            {
                "fields": (
                    "status",
                    "color",
                    "color_explanation",
                    "foss",
                    "legal_uncertainty",
                    "comment",
                )
            },
        ),
        (
            "Grants of rights",
            {"fields": ("patent_grant", "non_commmercial", "ethical_clause")},
        ),
    )


class GenericAdmin(admin.ModelAdmin):
    inlines = [ObligationInlineTab]
    list_display = ("name", "in_core", "metacategory", "team")
    list_filter = ["in_core"]
    ordering = ["in_core"]


class ComponentAdmin(admin.ModelAdmin):
    inlines = [VersionInlineTab]
    search_fields = ["name", "description"]


class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ("categories",)
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
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["spdx_valid_license_expr"].help_text = (
            "✔ License expression is not ambiguous"
            if not is_ambiguous(obj.spdx_valid_license_expr)
            else "❌ License expression is ambiguous : corrected license needs to be specified"
        )
        return form

    search_fields = ["purl"]


class UsageDecisionAdmin(admin.ModelAdmin):
    readonly_fields = ("decision_type",)


admin.site.register(License, LicenseAdmin)
admin.site.register(Obligation, ObligationAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Generic, GenericAdmin)
admin.site.register(Derogation)
admin.site.register(LicenseChoice, UsageDecisionAdmin)
admin.site.register(ExpressionValidation, UsageDecisionAdmin)
admin.site.register(Exploitation)
admin.site.register(Team)
