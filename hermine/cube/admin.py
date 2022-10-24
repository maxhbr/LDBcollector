# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django import forms
from django.contrib import admin

# Register your models here.

from .models import Product, ExpressionValidation, UsageDecision
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
from .models.policy import LicenseCuration
from .utils.licenses import is_ambiguous


class ObligationInline(admin.StackedInline):
    model = Obligation
    extra = 1
    ordering = ["generic"]


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
    autocomplete_fields = ("version",)
    model = Usage
    extra = 1


class LicenseAdmin(admin.ModelAdmin):
    inlines = [ObligationInline]
    list_display = ("spdx_id", "allowed", "status")
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
                    "copyleft",
                    "law_choice",
                    "venue_choice",
                    "liability",
                    "warranty",
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
                    "foss",
                    "osi_approved",
                    "fsf_approved",
                ),
            },
        ),
        (
            "Policy",
            {
                "fields": (
                    "status",
                    "allowed",
                    "allowed_explanation",
                    "comment",
                )
            },
        ),
        (
            "Conditions of use",
            {"fields": ("patent_grant", "non_commercial", "ethical_clause")},
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
    search_fields = ("release_number", "product__name")
    autocomplete_fields = ("product",)
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
        form.base_fields["spdx_valid_license_expr"].help_text += "<br/><br/>" + (
            "✔ This license expression is not ambiguous"
            if not is_ambiguous(obj.spdx_valid_license_expr)
            else "❌ License expression is ambiguous : corrected license needs to be specified"
        )
        return form

    search_fields = ["purl"]


class UsageDecisionAdmin(admin.ModelAdmin):
    readonly_fields = ("decision_type", "product_summary", "component_summary")
    list_display = ("__str__", "product_summary", "component_summary")
    autocomplete_fields = ("product", "release", "component", "version")
    fieldsets = (
        (
            "License",
            {
                "fields": (
                    "expression_in",
                    "expression_out",
                    "product_summary",
                    "component_summary",
                )
            },
        ),
        ("Update product conditions", {"fields": ("product", "release")}),
        (
            "Update component conditions",
            {"fields": ("component", "version", "scope")},
        ),
        ("Details", {"fields": ("explanation",)}),
    )

    @admin.display(description="Product")
    def product_summary(self, object):
        if object.release is not None:
            return object.release
        elif object.product is not None:
            return f"{object.product} (any release)"
        else:
            return "-"

    @admin.display(description="Component")
    def component_summary(self, object: UsageDecision):
        result = "-"
        if object.version is not None:
            result = object.version
        elif object.component:
            result = f"{object.component} (any version)"
        if object.scope:
            result = f"{result} ({object.scope} scope)"
        elif result != "-":
            result = f"{result} (any scope)"

        return result


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
admin.site.register(LicenseCuration, UsageDecisionAdmin)
admin.site.register(ExpressionValidation, UsageDecisionAdmin)
admin.site.register(LicenseChoice, UsageDecisionAdmin)
admin.site.register(Exploitation)
admin.site.register(Team)
