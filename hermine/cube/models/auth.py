#  SPDX-FileCopyrightText: 2025 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import binascii
import hashlib
import os

from django.conf import settings
from django.db import models


def hash_token_key(key: str) -> str:
    hasher = getattr(settings, "AUTH_TOKEN_HASH", "sha256")
    return getattr(hashlib, hasher)(key.encode()).hexdigest()


def make_token_key() -> str:
    return binascii.hexlify(os.urandom(20)).decode()


class Token(models.Model):
    """
    A token to authenticate a user
    """

    description = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="auth_token",
        on_delete=models.CASCADE,
        verbose_name="User",
    )
    key = models.TextField(
        unique=True, default=make_token_key, help_text="This will only be shown once"
    )
    created = models.DateTimeField(auto_now_add=True, editable=False)
    ttl = models.DurationField(
        verbose_name="Time to live",
        help_text="Duration in seconds of the token validity, empty for no limit",
        null=True,
        blank=True,
        default=getattr(settings, "AUTH_TOKEN_TTL", None),
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.key = hash_token_key(self.key)
        super().save(*args, **kwargs)

    @property
    def expiry(self):
        return self.created + self.ttl if self.ttl else "Never"

    def __str__(self):
        return f"{self.user} - {self.description}"

    class Meta:
        verbose_name = "API Token"
        verbose_name_plural = "API Tokens"
