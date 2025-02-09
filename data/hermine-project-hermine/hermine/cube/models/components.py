#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.db import models, transaction

from cube.utils.validators import validate_spdx_expression


class Usage(models.Model):
    """
    Qualifies how a Version of a component is used in a Release of a Product.
    """

    DEFAULT_PROJECT = "Default project"
    DEFAULT_SCOPE = "Default scope"

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
        (EXPLOITATION_DISTRIBUTION_BOTH, "Distribution as source code and non-source"),
        (EXPLOITATION_DISTRIBUTION_SOURCE, "Distribution as source code"),
        (EXPLOITATION_DISTRIBUTION_NONSOURCE, "Distribution as non source code"),
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
    LINKING_MINGLED = "Mingled"
    LINKING_CHOICES = [
        (LINKING_AGGREGATION, "Mere aggregation"),
        (LINKING_DYNAMIC, "Dynamic Linking"),
        (LINKING_STATIC, "Static Linking"),
        (LINKING_MINGLED, "Source code directly derived"),
    ]

    release = models.ForeignKey("Release", on_delete=models.CASCADE)
    version = models.ForeignKey("Version", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Unknown")
    addition_method = models.CharField(
        max_length=20, choices=ADDITION_CHOICES, blank=True
    )
    addition_date = models.DateTimeField(
        "Last updated", blank=True, null=True, auto_now=True
    )
    linking = models.CharField(
        max_length=20,
        choices=LINKING_CHOICES,
        blank=True,
        help_text="The type of linking between this component and the main code base",
    )
    component_modified = models.CharField(
        max_length=20,
        choices=MODIFICATION_CHOICES,
        blank=True,
        default=MODIFICATION_UNMODIFIED,
    )
    exploitation = models.CharField(
        max_length=50,
        choices=EXPLOITATION_CHOICES,
        blank=True,
        help_text="The way this component is distributed/exploited",
    )
    description = models.TextField(max_length=500, blank=True)
    licenses_chosen = models.ManyToManyField("License", blank=True)
    scope = models.CharField(max_length=50, default=DEFAULT_SCOPE)
    project = models.CharField(max_length=750, default=DEFAULT_PROJECT)
    license_expression = models.CharField(
        max_length=500,
        blank=True,
        validators=[validate_spdx_expression],
    )

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
    purl_type = models.CharField("purl package type", max_length=200, blank=True)
    description = models.TextField(max_length=500, blank=True)
    programming_language = models.CharField(max_length=200, blank=True)
    spdx_expression = models.CharField(max_length=200, blank=True)
    homepage_url = models.URLField(max_length=200, blank=True)
    export_control_status = models.CharField(
        max_length=20, choices=EXPORT_CHOICES, blank=True
    )

    def __str__(self):
        if self.purl_type:
            return f"{self.purl_type}/{self.name}"
        return self.name

    @property
    def namespace(self):
        if "/" not in self.name:
            return None

        return self.name.split("/")[0]

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "purl_type")


class Funding(models.Model):
    """
    A funding source of a third party component
    """

    component = models.ForeignKey(
        Component, on_delete=models.CASCADE, related_name="fundings"
    )
    url = models.URLField(max_length=200)
    type = models.CharField(max_length=200)

    def __str__(self):
        return self.url


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
        help_text="License expression concluded by analyzing tool (e.g. ORT)",
        validators=[validate_spdx_expression],
    )
    corrected_license = models.CharField(
        max_length=200,
        blank=True,
        help_text="Final license expression used in legal evaluation (required when validated expression is ambiguous or empty)",
    )
    purl = models.CharField(
        max_length=250,
        blank=True,
        help_text="Package URL (https://github.com/package-url/purl-spec)",
    )

    def save(self, *args, **kwargs):
        if self.pk is None:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            changed_license = (
                Version.objects.filter(pk=self.pk)
                .values_list("corrected_license", flat=True)
                .get()
                != self.corrected_license
            )

            if changed_license:
                Usage.objects.filter(version=self).update(license_expression="")
                Usage.licenses_chosen.through.objects.filter(
                    usage__version=self
                ).delete()
            return super().save(*args, **kwargs)

    @property
    def license_is_ambiguous(self):
        from cube.utils.spdx import is_ambiguous

        return not self.corrected_license and is_ambiguous(self.spdx_valid_license_expr)

    @property
    def imported_license(self):
        return self.spdx_valid_license_expr or self.declared_license_expr

    @property
    def effective_license(self):
        return self.corrected_license or self.spdx_valid_license_expr

    @property
    def licenses(self):
        """Get all licenses object listed in effective_license expression"""
        from cube.models import License
        from cube.utils.spdx import explode_spdx_to_units

        return License.objects.filter(
            spdx_id__in=[id for id in explode_spdx_to_units(self.effective_license)]
        )

    @property
    def curations(self):
        from cube.models.policy import LicenseCuration

        return LicenseCuration.objects.for_version(self)

    class Meta:
        ordering = ["component", "version_number"]
        unique_together = ["component", "version_number"]
        verbose_name = "Component version"
        verbose_name_plural = "Component versions"

    def __str__(self):
        return self.component.__str__() + ":" + self.version_number
