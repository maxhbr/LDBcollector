#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from social_core.backends.azuread_tenant import AzureADV2TenantOAuth2


class Entra(AzureADV2TenantOAuth2):
    """Azure ad authentication backend"""

    name = "azuread"

    def get_redirect_uri(self, state=None):
        """Build redirect_uri based on configured HOST (SOCIAL_AUTH_AZUREAD_HOST)"""
        host = self.setting("HOST", None)
        if host:
            self.redirect_uri = f"{host}/oauth/complete/{self.name}/"

        return super().get_redirect_uri(state)
