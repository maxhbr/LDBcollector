#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import argparse

from django.core.management import BaseCommand

from cube.utils.licenses import handle_licenses_json


class Command(BaseCommand):
    help = "Import licenses json file into Hermine"

    def add_arguments(self, parser):
        parser.add_argument(
            "--input-file",
            "-i",
            type=argparse.FileType("r", encoding="utf-8"),
            required=True,
        )

    def handle(self, *args, input_file, **options):
        handle_licenses_json(input_file)
