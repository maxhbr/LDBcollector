#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from cube.models import (
    Usage,
    Version,
)
from cube.utils.validators import validate_spdx_expression


class AbstractComponentRule(models.Model):
    component = models.ForeignKey(
        "Component", on_delete=models.CASCADE, blank=True, null=True
    )
    version = models.ForeignKey(
        "Version", on_delete=models.CASCADE, blank=True, null=True
    )

    @property
    def condition_display(self):
        if self.version is not None:
            return f"component: {self.version}"
        elif self.component:
            return f"component: {self.component} (any version)"
        else:
            return "component: any"

    def clean(self):
        """Model validation

        :meta private:
        """
        if self.component is not None and self.version is not None:
            raise ValidationError(
                "Rule can only apply to a component or a specific component version."
            )

        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


# Curations


class LicenseCurationManager(models.Manager):
    def for_version(self, version: Version):
        return self.filter(
            Q(component=version.component) | Q(component=None),
            Q(version=version) | Q(version=None),
            Q(expression_in=version.imported_license),
        )


class LicenseCuration(AbstractComponentRule):
    """
    A human decision to replace an imported license string with the correct SPDX expression
    """

    objects = LicenseCurationManager()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False
    )

    declared_expression = models.CharField(
        max_length=500,
        blank=True,
        help_text="The declared expression before any curation (used only for curation exports)",
    )

    expression_in = models.CharField(
        max_length=500,
        blank=True,
        help_text="The exact expression which must be changed",
    )
    expression_out = models.CharField(
        max_length=500,
        help_text="The expression which will replace `expression_in`",
        validators=[validate_spdx_expression],
    )

    explanation = models.TextField(max_length=500, blank=True, null=True)


class AbstractUsageRule(AbstractComponentRule):
    """
    A mixin for all models in this file to filter a decision by component or usage.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False
    )
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, blank=True, null=True
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, blank=True, null=True
    )
    release = models.ForeignKey(
        "Release", on_delete=models.CASCADE, blank=True, null=True
    )

    scope = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Leave blank to apply for any scope",
    )
    exploitation = models.CharField(
        max_length=50, blank=True, choices=Usage.EXPLOITATION_CHOICES
    )

    @property
    def condition_display(self):
        result = super().condition_display
        if self.release is not None:
            result += f" — product: {self.release}"
        elif self.product is not None:
            result += f" — product: {self.product} (any release)"
        if self.category is not None:
            result += f' — product : any in "{self.category}" category'
        else:
            result += " — product: any"

        if self.scope:
            return result + f" — scope: {self.scope}"
        else:
            return result + f" — scope: any"

    def clean(self):
        """Model validation

        :meta private:
        """
        if (
            (
                self.category is not None
                and (self.product is not None or self.release is not None)
            )
            or (
                self.product is not None
                and (self.category is not None or self.release is not None)
            )
            or (
                self.release is not None
                and (self.category is not None or self.product is not None)
            )
        ):
            raise ValidationError(
                "Rule can only apply to a category of product product, a specific product or a specific release."
            )

        return super().clean()

    class Meta:
        abstract = True


class AbstractUsageRuleManager(models.Manager):
    def for_usage(self, usage: Usage):
        return self.filter(
            Q(component=usage.version.component) | Q(component=None),
            Q(version=usage.version) | Q(version=None),
            Q(product=usage.release.product) | Q(product=None),
            Q(release=usage.release) | Q(release=None),
            Q(category__in=usage.release.product.categories.all()) | Q(category=None),
            Q(scope=usage.scope) | Q(scope=None),
            Q(exploitation=usage.exploitation) | Q(exploitation=""),
        )


class LicenseChoiceManager(AbstractUsageRuleManager):
    def for_usage(self, usage: Usage):
        return (
            super()
            .for_usage(usage)
            .filter(expression_in=usage.version.effective_license)
        )


class LicenseChoice(AbstractUsageRule, models.Model):
    """
    A choice of license for when a SPDX expressions contains ORs
    """

    objects = LicenseChoiceManager()

    expression_in = models.CharField(
        max_length=500,
        help_text="The exact expression which must be changed",
    )
    expression_out = models.CharField(
        max_length=500,
        help_text="The expression which will replace `expression_in`",
        validators=[validate_spdx_expression],
    )

    explanation = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.expression_in + " → " + self.expression_out

    class Meta:
        verbose_name = "License choice rule"
        verbose_name_plural = "License choice rules"


## derogation table


class DerogationManager(AbstractUsageRuleManager):
    def for_usage(self, usage: Usage):
        return (
            super()
            .for_usage(usage)
            .filter(
                Q(linking=usage.linking) | Q(linking=""),
                Q(modification=usage.component_modified) | Q(modification=""),
            )
        )


class Derogation(AbstractUsageRule, models.Model):
    """
    A derogation to policy allowing use of a license, which can be generalized to a component, a release or a product.
    """

    objects = DerogationManager()

    license = models.ForeignKey(
        "License", on_delete=models.CASCADE, related_name="derogations"
    )
    linking = models.CharField(max_length=20, choices=Usage.LINKING_CHOICES, blank=True)
    modification = models.CharField(
        max_length=20, choices=Usage.MODIFICATION_CHOICES, blank=True
    )
    justification = models.TextField(max_length=500, blank=True)

    @property
    def condition_display(self):
        result = super().condition_display

        if self.linking:
            return result + f" — linking: {self.linking}"
        else:
            return result + " — linking: any"

    def __str__(self):
        return self.license.__str__()
