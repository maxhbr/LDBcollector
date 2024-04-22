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
from .models import Funding
from .models import Version
from .models import Usage
from .models import License
from .models import Generic
from .models import Obligation
from .models import Derogation
from .models import LicenseChoice
from .models import Exploitation
from .models import Team
from .models import LicenseCuration
from .models.policy import AbstractUsageRule
from .utils.spdx import is_ambiguous


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


class FundingInlineTab(admin.TabularInline):
    model = Funding
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
            "Optional informations",
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
    inlines = [VersionInlineTab, FundingInlineTab]
    search_fields = ["name", "description"]


class FundingAdmin(admin.ModelAdmin):
    search_fields = ["url"]


class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ("categories",)
    search_fields = ["name", "description"]


class ReleaseAdmin(admin.ModelAdmin):
    search_fields = ("release_number", "product__name")
    autocomplete_fields = ("product",)
    inlines = [UsageInlineTab]


class UsageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "version")
    autocomplete_fields = (
        "release",
        "version",
    )
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

        if obj is None:
            return form

        form.base_fields["spdx_valid_license_expr"].help_text += "<br/><br/>" + (
            "✔ This license expression is not ambiguous"
            if not is_ambiguous(obj.spdx_valid_license_expr)
            else "❌ License expression is ambiguous : corrected license needs to be specified"
        )
        return form

    search_fields = ["purl"]


class ComponentRuleAdminMixin:
    @admin.display(description="Component")
    def component_summary(self, object: AbstractUsageRule):
        result = "-"
        if object.version is not None:
            result = object.version
        elif object.component:
            if object.version_constraint:
                result = f"{object.component} ({object.version_constraint})"
            else:
                result = f"{object.component} (any version)"

        return result


class LicenseCurationAdmin(ComponentRuleAdminMixin, admin.ModelAdmin):
    readonly_fields = (
        "created",
        "updated",
        "author",
        "component_summary",
    )
    list_display = ("__str__", "component_summary")
    autocomplete_fields = ("component", "version")

    fieldsets = (
        ("", {"fields": ("created", "updated", "author")}),
        (
            "License",
            {
                "fields": (
                    "expression_in",
                    "expression_out",
                )
            },
        ),
        (
            "Update component conditions",
            {
                "fields": (
                    "component_summary",
                    "component",
                    "version",
                    "version_constraint",
                )
            },
        ),
        ("Details", {"fields": ("explanation",)}),
    )


class UsageRuleAdminMixin(ComponentRuleAdminMixin):
    readonly_fields = (
        "created",
        "updated",
        "author",
        "product_summary",
        "component_summary",
    )
    list_display = ("__str__", "product_summary", "component_summary")
    autocomplete_fields = ("product", "release", "component", "version")

    @admin.display(description="Product")
    def product_summary(self, object):
        if object.category is not None:
            return f"Category: {object.category}"
        if object.release is not None:
            return object.release
        elif object.product is not None:
            return f"{object.product} (any release)"
        else:
            return "-"


class LicenseChoiceAdmin(UsageRuleAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("", {"fields": ("created", "updated", "author")}),
        (
            "License",
            {
                "fields": (
                    "expression_in",
                    "expression_out",
                )
            },
        ),
        (
            "Update product conditions",
            {"fields": ("product_summary", "category", "product", "release")},
        ),
        (
            "Update component conditions",
            {"fields": ("component_summary", "component", "version", "scope")},
        ),
        ("Details", {"fields": ("explanation",)}),
    )
    pass


class DerogationAdmin(UsageRuleAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("", {"fields": ("created", "updated", "author")}),
        (
            "License",
            {"fields": ("license",)},
        ),
        (
            "Update product conditions",
            {"fields": ("product_summary", "category", "product", "release")},
        ),
        (
            "Update component conditions",
            {"fields": ("component_summary", "component", "version", "scope")},
        ),
        (
            "Update usage conditions",
            {
                "fields": (
                    "linking",
                    "modification",
                    "exploitation",
                )
            },
        ),
        ("Details", {"fields": ("justification",)}),
    )


admin.site.register(License, LicenseAdmin)
admin.site.register(Obligation, ObligationAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Funding, FundingAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Generic, GenericAdmin)
admin.site.register(LicenseCuration, LicenseCurationAdmin)
admin.site.register(LicenseChoice, LicenseChoiceAdmin)
admin.site.register(Derogation, DerogationAdmin)
admin.site.register(Exploitation)
admin.site.register(Team)
