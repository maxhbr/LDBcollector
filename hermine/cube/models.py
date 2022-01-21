# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.db import models
from django.contrib.auth.models import User

# Constant for Usage and Derogation models

LINKING_CHOICES = [
    ("Aggregation", "Mere aggregation"),
    ("Dynamic", "Dynamic Linking"),
    ("Static", "Static Linking"),
    ("Package", "Package Manager"),
    ("Mingled", "Source code directly derived"),
]

SCOPE_MASK_CHOICES = [
    ("usage", "Only this usage"),
    ("release", "The whole release"),
    ("component", "Every usage of this component"),
    ("linking", "Every usage with this same linking"),
    ("scope", "Every usage with the same scope"),
    ("linkingscope", "Every usage with the same scope AND the same linking"),
]


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Release(models.Model):
    SHIPPING_CHOICES = [
        ("Archived", "Archived"),
        ("Active", "In developpement"),
        ("Published", "Published"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    release_number = models.CharField(max_length=200)
    ship_status = models.CharField(max_length=20, choices=SHIPPING_CHOICES, blank=True)
    pub_date = models.DateTimeField("date published", blank=True, null=True)
    # First unvalidated step : 5 = all are validated
    valid_step = models.IntegerField("Validation Step", blank=True, null=True)

    class Meta:
        unique_together = ["product", "release_number"]

    def __str__(self):
        return self.product.__str__() + " " + self.release_number


class Team(models.Model):
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Component(models.Model):
    """
    A third party Component, specified in a Version object.

    :ivar name: (String) Short descritpion of the Generic obligation. Unique.
    :ivar package_repo: (String) repository of the package
    :ivar description: (String) Longer descritpion of the Generic obligation.
    :ivar programming_language: (String) Name of programming languages used in this Component
    :ivar spdx_expression: (String) An expression of license for the component. Though, it should not be here : a Version should have it.
    :ivar homepage_url: (URL) Url of the repository of the component
    :ivar export_control_status: (String) A string specifying the export control status

    """

    CLEARED = "CL"
    TOBECHECKED = "TBC"
    CONFIRMED = "CONF"
    EXPORT_CHOICES = [
        (CLEARED, "Cleared"),
        (TOBECHECKED, "To check"),
        (CONFIRMED, "Confirmed"),
    ]
    name = models.CharField(max_length=200, unique=True)
    package_repo = models.CharField(max_length=200, blank=True)
    description = models.TextField(max_length=500, blank=True)
    programming_language = models.CharField(max_length=200, blank=True)
    spdx_expression = models.CharField(max_length=200, blank=True)
    homepage_url = models.URLField(max_length=200, blank=True)
    export_control_status = models.CharField(
        max_length=20, choices=EXPORT_CHOICES, blank=True
    )

    def __str__(self):
        return self.name


class Version(models.Model):

    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    version_number = models.CharField(max_length=200)
    declared_license_expr = models.CharField(max_length=200, blank=True)
    spdx_valid_license_expr = models.CharField(max_length=200, blank=True)
    corrected_license = models.CharField(max_length=200, blank=True)
    purl = models.CharField(max_length=250, blank=True)

    class Meta:
        unique_together = ["component", "version_number"]

    def __str__(self):
        return self.component.__str__() + ":" + self.version_number


class LicenseManager(models.Manager):
    def get_by_natural_key(self, spdx_id):
        return self.get(spdx_id=spdx_id)


class License(models.Model):
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="To check")
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


class Usage(models.Model):
    """    A class that allows to qualify how a Version of a component is used in a Release of the your project. 

    """

    STATUS_CHOICES = [
        ("Auto", "Auto validated"),
        ("Unknown", "Unknown"),
        ("Validated", "Validated"),
        ("KO", "Problem"),
        ("Fixed", "Problem solved"),
    ]
    ADDITION_CHOICES = [("Scan", "Added by scan"), ("Manual", "Added manually")]
    EXPLOITATION_CHOICES = [
        ("Distribution", "Distribution source and object"),
        ("DistributionSource", "Distribution - Source"),
        ("DistributionNonSource", "Distribution Non source"),
        ("NetworkAccess", "Network access"),
        ("InternalUse", "Internal use"),
    ]
    MODIFICATION_CHOICES = [("Altered", "Modified"), ("Unmodified", "Not modified")]

    release = models.ForeignKey(Release, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Unknown")
    addition_method = models.CharField(
        max_length=20, choices=ADDITION_CHOICES, blank=True
    )
    addition_date = models.DateTimeField("date added", blank=True, null=True)
    linking = models.CharField(max_length=20, choices=LINKING_CHOICES, blank=True)
    component_modified = models.CharField(
        max_length=20, choices=MODIFICATION_CHOICES, blank=True, default="Unmodified"
    )
    exploitation = models.CharField(
        max_length=50, choices=EXPLOITATION_CHOICES, default=EXPLOITATION_CHOICES[0][0]
    )
    description = models.TextField(max_length=500, blank=True)
    licenses_chosen = models.ManyToManyField(License, blank=True)
    scope = models.CharField(max_length=50, blank=True, null=True)
    license_expression = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.release.__str__() + " <=> " + self.version.__str__()


class Generic(models.Model):
    """A Generic obligation which is the simplification of the instances of several similar obligations.
    

    :ivar name: (String) Short descritpion of the Generic obligation. Unique.
    :ivar description: (String) Longer description, optional.
    :ivar in_core: (Boolean) If set to True, it means that this Generic obligation is assumed to systematically fit to the enterprise policy. Else, it means that it has to be manually checked.  
    :ivar metacategory: (String) A category of Generic oblgation.
    :ivar team: (Team) A foreign key to the competent Team.
    :ivar passivity: (String) A Generic obligation needs to conduct some kind of action (Active) or NOT to do specific things (Passive) 
    
    """

    PASSIVITY_CHOICES = [("Active", "Active"), ("Passive", "Passive")]
    METAGATEGORY_CHOICES = [
        ("Communication", "Communication constraints"),
        ("IPManagement", "IP management"),
        ("LicenseAgreement", "License Agreement"),
        ("Mentions", "Mentions"),
        ("ProvidingSourceCode", "Providing source code"),
        ("TechnicalConstraints", "Technical Constraints"),
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


class Obligation(models.Model):
    """An obligation deduced from a license verbatim. An obligation comes from only one license.

    :param models.Model: Django class to define models 
    :type models: models.Model
    :ivar license: (License) A foreign key to the License instance that implies the current obligation.
    :ivar generic: (Generic) An optional foreign key that links to the generic obligation. 
    :ivvar name: (String) Quick description of the Obligation.
    :ivar verbatim: (String) Full text of the obligation, out of the license itself.
    :ivar passivity: (String) A string that indicates if the type of obligation is "Active" (basically, under certain confition you SHOULD perform some action) or "Passive" (under certain concondition you SHOULD NOT do something)
    :ivar trigger_expl: (String) A string that indicates the context necessary to trigger this obligation
    :ivar trigger_mdf: (String) A string that indicates status of modication necessary to trigger this obligation
    """

    TRIGGER_EXPL_CHOICES = [
        ("Distribution", "Distribution Source or Object"),
        ("DistributionSource", "Distribution of Source Code"),
        ("DistributionNonSource", "Distribution Non Source"),
        ("NetworkAccess", "Network Access"),
        ("InternalUse", "Internal Use"),
    ]

    TRIGGER_MDF_CHOICES = [
        ("Altered", "Only if Modified"),
        ("Unmodified", "Only if Not Modified"),
        ("AlteredUnmodified", "Modified or Not"),
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
        max_length=40, choices=TRIGGER_EXPL_CHOICES, default="Distribution"
    )
    trigger_mdf = models.CharField(
        max_length=40, choices=TRIGGER_MDF_CHOICES, default="AlteredUnmodified"
    )

    def __str__(self):
        return self.license.__str__() + " -" + self.name


class Derogation(models.Model):

    license = models.ForeignKey(License, on_delete=models.CASCADE)
    release = models.ForeignKey(Release, on_delete=models.CASCADE, null=True)
    usage = models.ForeignKey(Usage, on_delete=models.CASCADE, blank=True, null=True)
    linking = models.CharField(
        max_length=20, choices=LINKING_CHOICES, blank=True, null=True
    )
    scope = models.CharField(
        max_length=50, choices=SCOPE_MASK_CHOICES, blank=True, null=True
    )
    justification = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.license.__str__() + " : " + str(self.release.id)


class LicenseChoice(models.Model):
    """ A class to store choices made for licenses

    """

    expression_in = models.CharField(max_length=500)
    expression_out = models.CharField(max_length=500)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True
    )
    release = models.ForeignKey(
        Release, on_delete=models.CASCADE, blank=True, null=True
    )
    component = models.ForeignKey(
        Component, on_delete=models.CASCADE, blank=True, null=True
    )
    version = models.ForeignKey(
        Version, on_delete=models.CASCADE, blank=True, null=True
    )

    scope = models.CharField(max_length=128, blank=True, null=True)

    explanation = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.expression_in + " => " + self.expression_out
