#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import json
import logging
import os
from json import JSONDecodeError

from django.core.management import BaseCommand
from django.core.management import call_command
from django.core.serializers import deserialize
from django.core.serializers.base import DeserializationError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Initialize the shared data, should be run once before startup
    """

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, filename, *args, **options):
        # Delete current shared database file
        os.remove("shared.sqlite3")
        # Run all migrations on the shared database
        call_command("migrate", database="shared", interactive=False, verbosity=0)

        # Read file and deserialize it
        with open(filename, "r") as f:
            filecontent = f.read()
            try:
                data = json.loads(filecontent)
            except JSONDecodeError:
                raise RuntimeError("The file is not a valid JSON file")

            if "date" not in data:
                logger.error('Shared database should have a "date" key')
            if "version" not in data:
                logger.error('Shared database should have a "version" key')
            if "objects" not in data:
                raise RuntimeError("Shared database has no 'objects' key")

            try:
                for obj in deserialize(
                    "python",
                    data["objects"],
                    using="shared",
                ):
                    obj.save(using="shared")

                self.stdout.write(self.style.SUCCESS("Shared database initialized"))

            except DeserializationError as e:
                raise RuntimeError(str(e))
