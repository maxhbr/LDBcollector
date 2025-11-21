#  SPDX-FileCopyrightText: 2023 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.conf import settings
from django.contrib.auth.middleware import (
    RemoteUserMiddleware as BaseRemoteUserMiddleware,
)


class RemoteUserMiddleware(BaseRemoteUserMiddleware):
    header = settings.REMOTE_USER_HEADER
