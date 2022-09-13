#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from cube.models import (
    Usage,
)


class UsageDecisionManager(models.Manager):
    def for_usage(self, usage: Usage):
        return self.filter(
            Q(component=usage.version.component) | Q(component=None),
            Q(version=usage.version) | Q(version=None),
            Q(product=usage.release.product) | Q(product=None),
            Q(release=usage.release) | Q(release=None),
            Q(scope=usage.scope) | Q(scope=None),
        )


class UsageDecision(models.Model):
    """
    A generic class to generalize choices made about usages and licenses to several versions, release or products.
    """

    LICENCE_CHOICE = "choice"
    EXPRESSION_VALIDATION = "validation"
    DECISION_TYPES = (
        (LICENCE_CHOICE, "Licence choice"),
        (EXPRESSION_VALIDATION, "Expression validation"),
    )

    decision_type = models.CharField(
        max_length=500, choices=DECISION_TYPES, blank=False
    )

    expression_in = models.CharField(max_length=500)
    expression_out = models.CharField(max_length=500)

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

    scope = models.CharField(max_length=128, blank=True, null=True)

    explanation = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.expression_in + " => " + self.expression_out

    def clean(self):
        if self.release is not None and self.product is not None:
            raise ValidationError(
                "Rule can only apply to a product or a specific release."
            )
        if self.component is not None and self.version is not None:
            raise ValidationError(
                "Rule can only apply to a component or a specific component version."
            )


class LicenseChoiceManager(UsageDecisionManager):
    def for_usage(self, usage: Usage):
        return (
            super()
            .for_usage(usage)
            .filter(expression_in=usage.version.effective_license)
        )

    def get_queryset(self):
        return super().get_queryset().filter(decision_type=UsageDecision.LICENCE_CHOICE)


class LicenseChoice(UsageDecision):
    """
    A choice of license for when a SPDX expressions contains ORs
    """

    objects = LicenseChoiceManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field("decision_type").default = UsageDecision.LICENCE_CHOICE
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "License choice rule"
        verbose_name_plural = "License choice rules"


class ExpressionValidationManager(UsageDecisionManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(decision_type=UsageDecision.EXPRESSION_VALIDATION)
        )


class ExpressionValidation(UsageDecision):
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


class Derogation(models.Model):
    """
    A release / usage specific derogation to policy allowing use of a license.
    """

    SCOPE_MASK_CHOICES = [
        ("usage", "Only this usage"),
        ("release", "The whole release"),
        ("component", "Every usage of this component"),
        ("linking", "Every usage with this same linking"),
        ("scope", "Every usage with the same scope"),
        ("linkingscope", "Every usage with the same scope AND the same linking"),
    ]

    license = models.ForeignKey("License", on_delete=models.CASCADE)
    release = models.ForeignKey("Release", on_delete=models.CASCADE, null=True)
    usage = models.ForeignKey("Usage", on_delete=models.CASCADE, blank=True, null=True)
    linking = models.CharField(
        max_length=20, choices=Usage.LINKING_CHOICES, blank=True, null=True
    )
    scope = models.CharField(
        max_length=50, choices=SCOPE_MASK_CHOICES, blank=True, null=True
    )
    justification = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.license.__str__() + " : " + str(self.release.id)
