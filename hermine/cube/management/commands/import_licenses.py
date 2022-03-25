#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import argparse

from django.core.management import BaseCommand

from cube.management.commands._base_commands import BaseImportCommand
from cube.utils.licenses import handle_licenses_json


class Command(BaseImportCommand):
    help = "Import licenses json file into Hermine"

    def handle(self, *args, input_file, **options):
        handle_licenses_json(input_file)
