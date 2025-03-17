#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.models import User
from django.db import models

from .components import Usage


class ReleaseConsultation(models.Model):
    """
    A consultation of a release by a user

    This model is used to track the number of consultations of a release by a user.
    """

    release = models.ForeignKey(
        "Release", on_delete=models.CASCADE, related_name="consultations"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} consulted {self.release}"

    class Meta:
        verbose_name = "Release consultation"
        verbose_name_plural = "Release consultations"
        unique_together = (("release", "user"),)


class SBOMImport(models.Model):
    BOM_ORT = "ORTBom"
    BOM_SPDX = "SPDXBom"
    BOM_CYCLONEDX = "CYCLONEDXBom"
    BOM_CHOICES = (
        (BOM_ORT, "ORT Evaluated model (JSON)"),
        (BOM_SPDX, "SPDX Bill of Materials"),
        (BOM_CYCLONEDX, "CycloneDX Bill of Materials (JSON)"),
    )

    IMPORT_MODE_MERGE = "Merge"
    IMPORT_MODE_REPLACE = "Replace"
    IMPORT_MODE_CHOICES = (
        (
            IMPORT_MODE_REPLACE,
            "Delete all previously saved component usages and remplace with new import",
        ),
        (IMPORT_MODE_MERGE, "Add new component usages while keeping previous ones"),
    )

    file_name = models.CharField(max_length=200, blank=True)
    file_type = models.CharField(max_length=12, choices=BOM_CHOICES, blank=True)
    mode = models.CharField(max_length=20, choices=IMPORT_MODE_CHOICES)
    linking = models.CharField(
        max_length=20,
        choices=Usage.LINKING_CHOICES,
        help_text="Linking type for the imported components",
    )
    date = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    release = models.ForeignKey(
        "Release", on_delete=models.CASCADE, related_name="import_history"
    )

    class Meta:
        verbose_name = "SBOM import"
        verbose_name_plural = "SBOM imports"
