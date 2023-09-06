#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.db import models
from django.contrib.auth.models import User

from cube.models import Release


class ReleaseConsultation(models.Model):
    """
    A consultation of a release by a user

    This model is used to track the number of consultations of a release by a user.
    """

    release = models.ForeignKey(
        Release, on_delete=models.CASCADE, related_name="consultations"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, auto_now=True)

    def __str__(self):
        return f"{self.user} consulted {self.release}"

    class Meta:
        verbose_name = "Release consultation"
        verbose_name_plural = "Release consultations"
        unique_together = (("release", "user"),)
