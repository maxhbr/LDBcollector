#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.db import models
from django.db.models import Q, F
from django.urls import reverse_lazy
from django.utils.functional import cached_property

from cube.models import Usage
from cube.utils.reference import license_reference_diff, generic_reference_diff


class LicenseManager(models.Manager):
    def get_by_natural_key(self, spdx_id):
        return self.get(spdx_id=spdx_id)


class License(models.Model):
    """
    A license identified by its SPDX id.


    """

    COPYLEFT_NONE = "None"
    COPYLEFT_STRONG = "Strong"
    COPYLEFT_WEAK = "Weak"
    COPYLEFT_NETWORK = "Network"
    COPYLEFT_NETWORK_WEAK = "NetworkWeak"
    COPYLEFT_CHOICES = [
        (COPYLEFT_NONE, "Permissive"),
        (COPYLEFT_STRONG, "Strong copyleft"),
        (COPYLEFT_WEAK, "Weak copyleft"),
        (COPYLEFT_NETWORK, "Strong network copyleft"),
        (COPYLEFT_NETWORK_WEAK, "Weak network copyleft"),
    ]
    ALLOWED_ALWAYS = "always"
    ALLOWED_NEVER = "never"
    ALLOWED_CONTEXT = "context"
    ALLOWED_NOTFOSS = "notfoss"
    ALLOWED_CHOICES = [
        (ALLOWED_ALWAYS, "Always allowed"),
        (ALLOWED_NEVER, "Never allowed"),
        (ALLOWED_CONTEXT, "Allowed depending on context"),
        (ALLOWED_NOTFOSS, "Out of FOSS Policy"),
        ("", "Not reviewed yet"),
    ]
    FOSS_YES = "Yes"
    FOSS_YES_AUTO = "Yes-Auto"
    FOSS_NO = "No"
    FOSS_NO_AUTO = "No-Auto"
    FOSS_CHOICES = [
        (FOSS_YES, "We consider it is FOSS"),
        (FOSS_YES_AUTO, "FOSS - deduced"),
        (FOSS_NO, "We consider it is NOT FOSS"),
        (FOSS_NO_AUTO, "NOT FOSS - deduced"),
    ]
    STATUS_CHECKED = "Checked"
    STATUS_PENDING = "Pending"
    STATUS_TO_DISCUSS = "To_Discuss"
    STATUS_TO_CHECK = "To_Check"
    STATUS_CHOICES = [
        (STATUS_CHECKED, "Checked"),
        (STATUS_PENDING, "Pending"),
        (STATUS_TO_DISCUSS, "To discuss"),
        (STATUS_TO_CHECK, "To check"),
    ]
    LIABILITY_FULL = "Full"
    LIABILITY_PARTIAL = "Partial"
    LIABILITY_ABSENT = "Absent"
    LIABILITY_CHOICES = [
        (LIABILITY_FULL, "Full clause"),
        (LIABILITY_PARTIAL, "Partial clause"),
        (LIABILITY_ABSENT, "No clause"),
    ]
    WARRANTY_FULL = "Full"
    WARRANTY_PARTIAL = "Partial"
    WARRANTY_ABSENT = "Absent"
    WARRANTY_CHOICES = [
        (WARRANTY_FULL, "Full clause"),
        (WARRANTY_PARTIAL, "Partial clause"),
        (WARRANTY_ABSENT, "No clause"),
    ]
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    spdx_id = models.CharField("SPDX Identifier", max_length=200, unique=True)
    status = models.CharField(
        "Review status",
        max_length=20,
        choices=STATUS_CHOICES,
        default="To check",
    )
    long_name = models.CharField("Name", max_length=200, blank=True)
    categories = models.CharField(max_length=200, blank=True)
    license_version = models.CharField(max_length=200, blank=True)
    radical = models.CharField(max_length=200, blank=True)
    autoupgrade = models.BooleanField(null=True)
    steward = models.CharField(max_length=200, blank=True)
    inspiration_spdx = models.CharField(
        max_length=200,
        blank=True,
        help_text="SPDX Identifier of another license which inspired this one",
    )
    inspiration = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="A Licence which inspired this one",
    )

    copyleft = models.CharField(max_length=20, choices=COPYLEFT_CHOICES, blank=True)
    allowed = models.CharField(
        "OSS Policy", max_length=20, choices=ALLOWED_CHOICES, blank=True
    )
    allowed_explanation = models.TextField(
        "OSS Policy explanation", max_length=1500, blank=True
    )
    url = models.URLField(max_length=200, blank=True)
    osi_approved = models.BooleanField(null=True, verbose_name="OSI Approved")
    fsf_approved = models.BooleanField(null=True, verbose_name="FSF Approved")
    foss = models.CharField(max_length=20, choices=FOSS_CHOICES, blank=True)
    patent_grant = models.BooleanField(null=True)
    ethical_clause = models.BooleanField(null=True)
    non_commercial = models.BooleanField("Only non-commercial use", null=True)
    non_tivoisation = models.BooleanField(null=True)
    liability = models.CharField(
        "Limitation of Liability", max_length=30, choices=LIABILITY_CHOICES, blank=True
    )
    warranty = models.CharField(
        "Disclaimer of Warranty",
        max_length=30,
        choices=WARRANTY_CHOICES,
        blank=True,
    )
    law_choice = models.CharField(max_length=200, blank=True)
    venue_choice = models.CharField(max_length=200, blank=True)
    comment = models.TextField(max_length=1500, blank=True)
    verbatim = models.TextField(
        "Exact text of the license",
        blank=True,
        help_text="Only necessary if the license has no official SPDX ID",
    )
    objects = LicenseManager()

    def natural_key(self):
        return (self.spdx_id,)

    @property
    def is_core_covered(self):
        return not self.obligation_set.filter(
            Q(generic__isnull=True) | Q(generic__in_core=False)
        ).exists()

    @property
    def context_derogations(self):
        from cube.models import Derogation

        return Derogation.objects.filter(license=self).filter(
            release=None, product=None
        )

    @cached_property
    def reference_diff(self):
        return license_reference_diff(self)

    def product_derogations(self):
        from cube.models import Derogation

        return Derogation.objects.filter(license=self).exclude(
            product=None, release=None
        )

    def get_absolute_url(self):
        return reverse_lazy("cube:license", args=[self.id])

    def __str__(self):
        return self.spdx_id

    class Meta:
        ordering = ("spdx_id",)
        verbose_name = "License"
        verbose_name_plural = "Licenses"
        permissions = (
            ("export_license", "Can export licenses"),
            ("import_license", "Can import licenses"),
        )


class TeamManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Team(models.Model):
    """
    A team assigned to generics obligations.
    """

    objects = TeamManager()

    name = models.CharField(max_length=200, unique=True)
    icon = models.CharField(max_length=200, null=True, blank=True)

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name


class GenericManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Generic(models.Model):
    """A Generic obligation which is the simplification of the instances of several
    similar :class `Obligation`."""

    objects = GenericManager()
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    PASSIVITY_CHOICES = [("Active", "Active"), ("Passive", "Passive")]
    METAGATEGORY_CHOICES = [
        ("Communication", "Communication constraints"),
        ("IPManagement", "IP management"),
        ("LicenseAgreement", "License agreement"),
        ("Mentions", "Mentions"),
        ("ProvidingSourceCode", "Providing source code"),
        ("TechnicalConstraints", "Technical constraints"),
    ]

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Short description of the Generic obligation. Unique.",
    )
    description = models.TextField(
        max_length=500, blank=True, help_text="Longer description, optional."
    )
    in_core = models.BooleanField(
        default=False,
        help_text="If True, means this Generic obligation is assumed to systematically fit to the enterprise policy. "
        "Otherwise, means it has to be manually checked.",
    )
    metacategory = models.CharField(
        max_length=40,
        choices=METAGATEGORY_CHOICES,
        blank=True,
        help_text="A category of Generic obligation.",
    )
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    passivity = models.CharField(
        max_length=20,
        choices=PASSIVITY_CHOICES,
        blank=True,
        help_text="A Generic obligation needs to conduct some kind of action"
        "(Active) or NOT to do specific things (Passive)",
    )

    @cached_property
    def reference_diff(self):
        return generic_reference_diff(self)

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return ("[Core]" if self.in_core else "") + self.name

    class Meta:
        verbose_name = "Generic obligation"
        verbose_name_plural = "Generic obligations"
        permissions = (
            ("export_generic", "Can export generic obligations"),
            ("import_generic", "Can import generic obligations"),
        )


class ObligationManager(models.Manager):
    def get_by_natural_key(self, name, license_spdx_id):
        return self.get(name=name, license__spdx_id=license_spdx_id)


class Obligation(models.Model):
    """An obligation deduced from a license verbatim. An obligation comes from only one
    license."""

    objects = ObligationManager()

    TRIGGER_EXPL_CHOICES = [
        (
            Usage.EXPLOITATION_DISTRIBUTION_BOTH,
            "If the component is distributed as source code or as binary",
        ),
        (
            Usage.EXPLOITATION_DISTRIBUTION_SOURCE,
            "If the component is distributed as source code",
        ),
        (
            Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            "If the component is distributed as binary",
        ),
        (Usage.EXPLOITATION_NETWORK, "If component is accessible by network access"),
        (Usage.EXPLOITATION_INTERNAL, "If the component is used internally"),
    ]

    TRIGGER_MDF_CHOICES = [
        (Usage.MODIFICATION_ALTERED, "Only if the component is modified"),
        (Usage.MODIFICATION_UNMODIFIED, "Only if the component is not modified"),
        (
            Usage.MODIFICATION_ALTERED + Usage.MODIFICATION_UNMODIFIED,
            "Whether the component is modified or not",
        ),
    ]

    PASSIVITY_CHOICES = [("Active", "Active"), ("Passive", "Passive")]

    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        help_text="The License instance that implies the current obligation.",
    )
    generic = models.ForeignKey(
        Generic, on_delete=models.PROTECT, blank=True, null=True
    )
    name = models.CharField(max_length=200)
    verbatim = models.TextField(
        max_length=4000,
        help_text="Full text of the obligation, out of the license itself",
    )
    passivity = models.CharField(
        max_length=20,
        choices=PASSIVITY_CHOICES,
        blank=True,
        help_text='If the obligation is "Active" (under certain condition you SHOULD perform some action) or'
        '"Passive" (under certain condition you SHOULD NOT do something)',
    )

    trigger_expl = models.CharField(
        max_length=40,
        choices=TRIGGER_EXPL_CHOICES,
        default=Usage.EXPLOITATION_DISTRIBUTION_BOTH,
        verbose_name="Triggering exploitation context",
        help_text="The context necessary to trigger this obligation",
    )
    trigger_mdf = models.CharField(
        max_length=40,
        choices=TRIGGER_MDF_CHOICES,
        default=Usage.MODIFICATION_ANY,
        verbose_name="Triggering modifications",
        help_text="Status of modication necessary to trigger this obligation",
    )

    def natural_key(self):
        return (self.name,) + self.license.natural_key()

    class Meta:
        unique_together = ["name", "license"]
        ordering = [F("generic__metacategory").desc(nulls_last=True)]

    def __str__(self):
        return self.license.__str__() + " -" + self.name
