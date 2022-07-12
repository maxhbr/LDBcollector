#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.models import User


class ForceLoginMixin:
    def setUp(self):
        self.client.force_login(User.objects.get(username="admin"))
