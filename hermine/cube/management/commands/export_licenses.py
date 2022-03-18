#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import argparse
import sys

from django.core.management import BaseCommand

from cube.utils.licenses import export_licenses


class Command(BaseCommand):
    help = "Export licenses to JSON"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output_file", "-o", type=argparse.FileType("w", encoding="utf-8")
        )
        parser.add_argument(
            "--beautify", "-b", action="store_true", help="Indent output"
        )

    def handle(self, *args, output_file=None, beautify=False, **options):
        if output_file is None:
            output_file = sys.stdout

        output_file.write(export_licenses(indent=beautify))
