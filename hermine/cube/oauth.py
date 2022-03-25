#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from urllib.parse import urlencode

from django.conf import settings
from social_core.backends.oauth import BaseOAuth2


class OAuth2(BaseOAuth2):
    """GitHub OAuth authentication backend"""

    def auth_html(self):
        pass

    name = "default"
    AUTHORIZATION_URL = settings.OAUTH_CLIENT["authorize_url"]
    ACCESS_TOKEN_URL = settings.OAUTH_CLIENT["access_token_url"]

    def get_user_details(self, response):
        return settings.OAUTH_CLIENT["user_details"](response)

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        return self.get_json(
            settings.OAUTH_CLIENT["user_url"],
            headers={"Authorization": f"token {access_token}"},
        )
