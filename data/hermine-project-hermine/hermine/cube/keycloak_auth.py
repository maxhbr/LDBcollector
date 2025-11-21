#  SPDX-FileCopyrightText: 2021
#
#  SPDX-License-Identifier: AGPL-3.0-only
# social_core.backends.keycloak.KeycloakOAuth2

from social_core.backends.keycloak import KeycloakOAuth2


class KeycloakBackend(KeycloakOAuth2):
    """Keycloak ad authentication backend"""

    name = "keycloak"

    def get_redirect_uri(self, state=None):
        """Build redirect_uri based on configured HOST"""
        host = self.setting("HOST", None)
        if host:
            self.redirect_uri = f"{host}/oauth/complete/{self.name}/"

        return super().get_redirect_uri(state)
