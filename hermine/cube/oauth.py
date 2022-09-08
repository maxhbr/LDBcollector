#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from urllib.parse import urlencode

from django.conf import settings
from social_core.backends.oauth import BaseOAuth2


class OAuth2(BaseOAuth2):
    """OAuth2 authentication backend"""

    def auth_html(self):
        pass

    name = "default"
    AUTHORIZATION_URL = settings.OAUTH_CLIENT["authorize_url"]
    ACCESS_TOKEN_URL = settings.OAUTH_CLIENT["access_token_url"]
    ID_KEY = settings.OAUTH_CLIENT.get("id_key", "id")
    ACCESS_TOKEN_METHOD = settings.OAUTH_CLIENT.get("access_token_method", "POST")

    def get_scope(self):
        return settings.OAUTH_CLIENT.get("scopes", "openid profile")

    def get_user_details(self, response):
        return settings.OAUTH_CLIENT["user_details"](response)

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        return self.get_json(
            settings.OAUTH_CLIENT["user_url"],
            headers={"Authorization": f"bearer {access_token}"},
        )
