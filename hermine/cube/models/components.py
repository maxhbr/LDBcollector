#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.db import models


class Usage(models.Model):
    """
    Qualifies how a Version of a component is used in a Release of a Product.
    """

    STATUS_AUTO = "Auto"
    STATUS_UNKNOWN = "Unknown"
    STATUS_VALIDATED = "Validated"
    STATUS_KO = "KO"
    STATUS_FIXED = "Fixed"
    STATUS_CHOICES = [
        (STATUS_AUTO, "Auto validated"),
        (STATUS_UNKNOWN, "Unknown"),
        (STATUS_VALIDATED, "Validated"),
        (STATUS_KO, "Problem"),
        (STATUS_FIXED, "Problem solved"),
    ]
    ADDITION_SCAN = "Scan"
    ADDITION_MANUAL = "Manual"
    ADDITION_CHOICES = [
        (ADDITION_SCAN, "Added by scan"),
        (ADDITION_MANUAL, "Added manually"),
    ]

    EXPLOITATION_DISTRIBUTION_SOURCE = "DistributionSource"
    EXPLOITATION_DISTRIBUTION_NONSOURCE = "DistributionNonSource"
    EXPLOITATION_DISTRIBUTION_BOTH = (
        EXPLOITATION_DISTRIBUTION_SOURCE + EXPLOITATION_DISTRIBUTION_NONSOURCE
    )
    EXPLOITATION_NETWORK = "NetworkAccess"
    EXPLOITATION_INTERNAL = "InternalUse"
    EXPLOITATION_CHOICES = [
        (EXPLOITATION_DISTRIBUTION_BOTH, "Distribution source and object"),
        (EXPLOITATION_DISTRIBUTION_SOURCE, "Distribution - Source"),
        (EXPLOITATION_DISTRIBUTION_NONSOURCE, "Distribution Non source"),
        (EXPLOITATION_NETWORK, "Network access"),
        (EXPLOITATION_INTERNAL, "Internal use"),
    ]

    MODIFICATION_ALTERED = "Altered"
    MODIFICATION_UNMODIFIED = "Unmodified"
    MODIFICATION_ANY = MODIFICATION_ALTERED + MODIFICATION_UNMODIFIED
    MODIFICATION_CHOICES = [
        (MODIFICATION_ALTERED, "Modified"),
        (MODIFICATION_UNMODIFIED, "Not modified"),
    ]

    LINKING_AGGREGATION = "Aggregation"
    LINKING_DYNAMIC = "Dynamic"
    LINKING_STATIC = "Static"
    LINKING_PACKAGE = "Package"
    LINKING_MINGLED = "Mingled"
    LINKING_CHOICES = [
        (LINKING_AGGREGATION, "Mere aggregation"),
        (LINKING_DYNAMIC, "Dynamic Linking"),
        (LINKING_STATIC, "Static Linking"),
        (LINKING_PACKAGE, "Package Manager"),
        (LINKING_MINGLED, "Source code directly derived"),
    ]

    release = models.ForeignKey("Release", on_delete=models.CASCADE)
    version = models.ForeignKey("Version", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Unknown")
    addition_method = models.CharField(
        max_length=20, choices=ADDITION_CHOICES, blank=True
    )
    addition_date = models.DateTimeField("date added", blank=True, null=True)
    linking = models.CharField(max_length=20, choices=LINKING_CHOICES, blank=True)
    component_modified = models.CharField(
        max_length=20,
        choices=MODIFICATION_CHOICES,
        blank=True,
        default=MODIFICATION_UNMODIFIED,
    )
    exploitation = models.CharField(
        max_length=50, choices=EXPLOITATION_CHOICES, default=EXPLOITATION_CHOICES[0][0]
    )
    description = models.TextField(max_length=500, blank=True)
    licenses_chosen = models.ManyToManyField("License", blank=True)
    scope = models.CharField(max_length=50, blank=True)
    project = models.CharField(max_length=750, blank=True)
    license_expression = models.CharField(max_length=500, blank=True)

    @property
    def license_curations(self):
        from cube.models.policy import LicenseCuration

        return LicenseCuration.objects.for_usage(self)

    @property
    def expression_validations(self):
        from cube.models.policy import ExpressionValidation

        return ExpressionValidation.objects.for_usage(self)

    @property
    def license_choices(self):
        from cube.models.policy import LicenseChoice

        return LicenseChoice.objects.for_usage(self)

    def __str__(self):
        return self.release.__str__() + " <=> " + self.version.__str__()

    class Meta:
        verbose_name = "Component usage"
        verbose_name_plural = "Component usages"


class Component(models.Model):
    """A third party FOSS Component."""

    CLEARED = "CL"
    TOBECHECKED = "TBC"
    CONFIRMED = "CONF"
    EXPORT_CHOICES = [
        (CLEARED, "Cleared"),
        (TOBECHECKED, "To check"),
        (CONFIRMED, "Confirmed"),
    ]
    name = models.CharField(
        max_length=200, help_text="Unique name of the FOSS component."
    )
    package_repo = models.CharField("Package repository", max_length=200, blank=True)
    description = models.TextField(max_length=500, blank=True)
    programming_language = models.CharField(max_length=200, blank=True)
    spdx_expression = models.CharField(max_length=200, blank=True)
    homepage_url = models.URLField(max_length=200, blank=True)
    export_control_status = models.CharField(
        max_length=20, choices=EXPORT_CHOICES, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "package_repo")


class Version(models.Model):
    """
    A specific version of a third party component
    """

    component = models.ForeignKey(
        Component, on_delete=models.CASCADE, related_name="versions"
    )
    version_number = models.CharField(max_length=200)
    declared_license_expr = models.CharField(
        max_length=200,
        blank=True,
        help_text="Declared license expression (may not be SPDX valid)",
    )
    spdx_valid_license_expr = models.CharField(
        max_length=200,
        blank=True,
        help_text="License expression validated by user",
    )
    corrected_license = models.CharField(
        max_length=200,
        blank=True,
        help_text="Final license expression used in legal evaluation (required when validated expression is ambiguous)",
    )
    purl = models.CharField(
        max_length=250,
        blank=True,
        help_text="Package URL (https://github.com/package-url/purl-spec)",
    )

    @property
    def license_is_ambiguous(self):
        from cube.utils.licenses import is_ambiguous

        return not self.corrected_license and is_ambiguous(self.spdx_valid_license_expr)

    @property
    def effective_license(self):
        return self.corrected_license or self.spdx_valid_license_expr

    class Meta:
        unique_together = ["component", "version_number"]

    def __str__(self):
        return self.component.__str__() + ":" + self.version_number

    class Meta:
        verbose_name = "Component version"
        verbose_name_plural = "Component versions"
