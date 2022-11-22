#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from cube.models import (
    Usage,
)
from cube.utils.validators import validate_spdx_expression


class PolicyMixin(models.Model):
    """
    A mixin for all models in this file to filter a decision by component or usage.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, blank=True, null=True
    )
    release = models.ForeignKey(
        "Release", on_delete=models.CASCADE, blank=True, null=True
    )
    component = models.ForeignKey(
        "Component", on_delete=models.CASCADE, blank=True, null=True
    )
    version = models.ForeignKey(
        "Version", on_delete=models.CASCADE, blank=True, null=True
    )
    scope = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Leave blank to apply for any scope",
    )

    @property
    def condition_display(self):
        result = ""
        if self.release is not None:
            result += f"product: {self.release} — "
        elif self.product is not None:
            result += f"product: {self.product} (any release) — "
        else:
            result += "product: any — "

        if self.version is not None:
            result += f"component: {self.version}"
        elif self.component:
            result += f"component: {self.component} (any version)"
        else:
            result += "component: any"

        if self.scope:
            return result + f" — scope: {self.scope}"
        else:
            return result + f" — scope: any"

    def clean(self):
        """Model validation

        :meta private:
        """
        if self.release is not None and self.product is not None:
            raise ValidationError(
                "Rule can only apply to a product or a specific release."
            )
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


class UsageConditionManager(models.Manager):
    def for_usage(self, usage: Usage):
        return self.filter(
            Q(component=usage.version.component) | Q(component=None),
            Q(version=usage.version) | Q(version=None),
            Q(product=usage.release.product) | Q(product=None),
            Q(release=usage.release) | Q(release=None),
            Q(scope=usage.scope) | Q(scope=None),
        )


## usagedecision table


class UsageDecision(PolicyMixin, models.Model):
    """
    A generic class to generalize licenses curations, disambiguation or choices to
    several versions, releases or products.
    """

    objects = UsageConditionManager()

    LICENSE_CHOICE = "choice"
    EXPRESSION_VALIDATION = "validation"
    LICENSE_CURATION = "curation"
    DECISION_TYPES = (
        (LICENSE_CHOICE, "License choice"),
        (EXPRESSION_VALIDATION, "Expression validation"),
        (LICENSE_CURATION, "License curation"),
    )

    decision_type = models.CharField(
        max_length=500, choices=DECISION_TYPES, blank=False
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

    def __str__(self):
        return self.expression_in or "(blank)" + " → " + self.expression_out


class LicenseChoiceManager(UsageConditionManager):
    def for_usage(self, usage: Usage):
        return (
            super()
            .for_usage(usage)
            .filter(expression_in=usage.version.effective_license)
        )

    def get_queryset(self):
        return super().get_queryset().filter(decision_type=UsageDecision.LICENSE_CHOICE)


class LicenseChoice(UsageDecision):
    """
    A choice of license for when a SPDX expressions contains ORs
    """

    objects = LicenseChoiceManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field("decision_type").default = UsageDecision.LICENSE_CHOICE
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "License choice rule"
        verbose_name_plural = "License choice rules"


class ComponentDecisionManager(UsageConditionManager):
    def create(
        self,
        release=None,
        release_id=None,
        product=None,
        product_id=None,
        scope=None,
        **kwargs,
    ):
        if release is not None or release_id is not None:
            raise ValidationError("Release field must be empty.")
        if product is not None or product_id is not None:
            raise ValidationError("Product field must be empty.")
        if scope is not None:
            raise ValidationError("Scope field must be empty.")
        return super().create(**kwargs)


class ComponentDecisionMixin(models.Model):
    def clean(self):
        if self.release:
            raise ValidationError("Release field must be empty.")
        if self.product:
            raise ValidationError("Product field must be empty.")
        if self.scope:
            raise ValidationError("Scope field must be empty.")
        return super().clean()

    class Meta:
        abstract = True


class ExpressionValidationManager(ComponentDecisionManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(decision_type=UsageDecision.EXPRESSION_VALIDATION)
        )


class ExpressionValidation(ComponentDecisionMixin, UsageDecision):
    """
    A human decision about an ambiguous SPDX expression
    (typically contains only ANDs which could be badly registered ORs)
    """

    objects = ExpressionValidationManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field(
            "decision_type"
        ).default = UsageDecision.EXPRESSION_VALIDATION
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True


class LicenseCurationManager(ComponentDecisionManager):
    def get_queryset(self):
        return (
            super().get_queryset().filter(decision_type=UsageDecision.LICENSE_CURATION)
        )


class LicenseCuration(ComponentDecisionMixin, UsageDecision):
    """
    A human decision to replace an imported license string with the correct SPDX valid expression
    """

    objects = LicenseCurationManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field("decision_type").default = UsageDecision.LICENSE_CURATION
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True


## derogation table


class DerogationManager(UsageConditionManager):
    def for_usage(self, usage: Usage):
        return (
            super()
            .for_usage(usage)
            .filter(
                Q(linking=usage.linking) | Q(linking=""),
                Q(modification=usage.component_modified) | Q(modification=""),
                Q(exploitation=usage.exploitation) | Q(exploitation=""),
            )
        )


class Derogation(PolicyMixin, models.Model):
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
    exploitation = models.CharField(
        max_length=50, choices=Usage.EXPLOITATION_CHOICES, blank=True
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
