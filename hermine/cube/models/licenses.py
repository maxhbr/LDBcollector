#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.db import models

from cube.models import Usage


class LicenseManager(models.Manager):
    def get_by_natural_key(self, spdx_id):
        return self.get(spdx_id=spdx_id)


class License(models.Model):
    """
    A license identified by its SPDX id.
    """

    COPYLEFT_CHOICES = [
        ("None", "Persmissive"),
        ("Strong", "Strong copyleft"),
        ("Weak", "Weak copyleft"),
        ("Network", "Strong network copyleft"),
        ("NetworkWeak", "Weak network copyleft"),
    ]
    COLOR_CHOICES = [
        ("Green", "Always allowed"),
        ("Red", "Never allowed"),
        ("Orange", "Allowed depending on context"),
        ("Grey", "No reviewed yet"),
    ]
    FOSS_CHOICES = [
        ("Yes", "We consider it is FOSS"),
        ("Yes-Auto", "FOSS - deduced"),
        ("No", "We consider it is NOT FOSS"),
        ("No-Auto", "NOT FOSS - deduced"),
    ]
    STATUS_CHOICES = [
        ("Checked", "Checked"),
        ("Pending", "Pending"),
        ("To_Discuss", "To discuss"),
        ("To_Check", "To check"),
    ]

    spdx_id = models.CharField(max_length=200, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="To check",
        help_text="The review status of the license",
    )
    long_name = models.CharField(max_length=200, blank=True)
    categories = models.CharField(max_length=200, blank=True)
    license_version = models.CharField(max_length=200, blank=True)
    radical = models.CharField(max_length=200, blank=True)
    autoupgrade = models.BooleanField(null=True)
    steward = models.CharField(max_length=200, blank=True)
    inspiration_spdx = models.CharField(max_length=200, null=True, blank=True)
    inspiration = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    copyleft = models.CharField(max_length=20, choices=COPYLEFT_CHOICES, blank=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default="Grey")
    color_explanation = models.CharField(max_length=200, blank=True)
    url = models.URLField(max_length=200, blank=True)
    osi_approved = models.BooleanField(null=True)
    fsf_approved = models.BooleanField(null=True)
    foss = models.CharField(max_length=20, choices=FOSS_CHOICES, blank=True)
    patent_grant = models.BooleanField(null=True)
    ethical_clause = models.BooleanField(null=True)
    non_commmercial = models.BooleanField("Only non-commercial use", null=True)
    legal_uncertainty = models.BooleanField(null=True)
    non_tivoisation = models.BooleanField(null=True)
    technical_nature_constraint = models.BooleanField(null=True)
    law_choice = models.CharField(max_length=200, blank=True)
    venue_choice = models.CharField(max_length=200, blank=True)
    comment = models.TextField(max_length=1500, blank=True)
    verbatim = models.TextField(blank=True)
    objects = LicenseManager()

    def natural_key(self):
        return self.spdx_id

    def __str__(self):
        return self.spdx_id

    class Meta:
        ordering = ("spdx_id",)


class Team(models.Model):
    """
    A team assigned to generics obligations.
    """

    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Generic(models.Model):
    """
    A Generic obligation which is the simplification of the instances of several
    similar obligations.

    :ivar name: (String) Short descritpion of the Generic obligation. Unique.
    :ivar description: (String) Longer description, optional.
    :ivar in_core: (Boolean) If set to True, it means that this Generic obligation is
        assumed to systematically fit to the enterprise policy.
        Otherwise, it means that it has to be manually checked.
    :ivar metacategory: (String) A category of Generic oblgation.
    :ivar team: (Team) A foreign key to the competent Team.
    :ivar passivity: (String) A Generic obligation needs to conduct some kind of action
        (Active) or NOT to do specific things (Passive)
    """

    PASSIVITY_CHOICES = [("Active", "Active"), ("Passive", "Passive")]
    METAGATEGORY_CHOICES = [
        ("Communication", "Communication constraints"),
        ("IPManagement", "IP management"),
        ("LicenseAgreement", "License agreement"),
        ("Mentions", "Mentions"),
        ("ProvidingSourceCode", "Providing source code"),
        ("TechnicalConstraints", "Technical constraints"),
    ]
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    in_core = models.BooleanField(default=False)
    metacategory = models.CharField(
        max_length=40, choices=METAGATEGORY_CHOICES, blank=True
    )
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    passivity = models.CharField(max_length=20, choices=PASSIVITY_CHOICES, blank=True)

    def __str__(self):
        return ("[Core]" if self.in_core else "") + self.name

    class Meta:
        verbose_name = "Generic obligation"
        verbose_name_plural = "Generic obligations"


class Obligation(models.Model):
    """
    An obligation deduced from a license verbatim. An obligation comes from only one
    license.

    :param models.Model: Django class to define models
    :type models: models.Model
    :ivar license: (License) A foreign key to the License instance that implies the
        current obligation.
    :ivar generic: (Generic) An optional foreign key that links to the generic
        obligation.
    :ivvar name: (String) Quick description of the Obligation.
    :ivar verbatim: (String) Full text of the obligation, out of the license itself.
    :ivar passivity: (String) A string that indicates if the type of obligation is
        "Active" (basically, under certain confition you SHOULD perform some action) or
        "Passive" (under certain concondition you SHOULD NOT do something)
    :ivar trigger_expl: (String) A string that indicates the context necessary to
        trigger this obligation
    :ivar trigger_mdf: (String) A string that indicates status of modication necessary
        to trigger this obligation
    """

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

    license = models.ForeignKey(License, on_delete=models.CASCADE)
    generic = models.ForeignKey(
        Generic, on_delete=models.PROTECT, blank=True, null=True
    )
    name = models.CharField(max_length=200)
    verbatim = models.TextField(max_length=4000)
    passivity = models.CharField(max_length=20, choices=PASSIVITY_CHOICES, blank=True)

    trigger_expl = models.CharField(
        max_length=40,
        choices=TRIGGER_EXPL_CHOICES,
        default=Usage.EXPLOITATION_DISTRIBUTION_BOTH,
    )
    trigger_mdf = models.CharField(
        max_length=40,
        choices=TRIGGER_MDF_CHOICES,
        default=Usage.MODIFICATION_ANY,
    )

    class Meta:
        unique_together = ["name", "license"]

    def __str__(self):
        return self.license.__str__() + " -" + self.name
