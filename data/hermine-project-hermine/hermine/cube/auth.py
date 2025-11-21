#  SPDX-FileCopyrightText: 2025 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from cube.models import Token
from cube.models.auth import hash_token_key


class HashedTokenAuthentication(TokenAuthentication):
    """
    Token based authentication using the Django Rest Framework Token model.
    """

    model = Token

    def authenticate_credentials(self, key):
        key = hash_token_key(key)
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token.")

        if token.ttl is not None and token.created + token.ttl < timezone.now():
            raise exceptions.AuthenticationFailed("Token has expired.")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted.")

        return (token.user, token)
