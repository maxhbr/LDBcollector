# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-License-Identifier: AGPL-3.0-only

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    """
    Create a superuser if none exist
    Example:
        manage.py createsuperuser_if_none_exists --user=admin --password=changeme
    """

    def add_arguments(self, parser):
        parser.add_argument("--user", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--email", default="admin@example.com")

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.exists():
            return

        username = options["user"]
        password = options["password"]
        email = options["email"]

        User.objects.create_superuser(username=username, password=password, email=email)

        self.stdout.write(f'Local user "{username}" was created')
