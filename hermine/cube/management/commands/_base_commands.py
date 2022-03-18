#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import argparse
import sys

from django.core.management import BaseCommand


class BaseExportCommand(BaseCommand):
    beautify = False

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-file", "-o", type=argparse.FileType("w", encoding="utf-8")
        )
        parser.add_argument(
            "--beautify", "-b", action="store_true", help="Indent output"
        )

    def handle(self, *args, output_file=None, beautify=False, **options):
        self.beautify = beautify

        if output_file is None:
            output_file = sys.stdout

        output_file.write(self.get_data())

    def get_data(self):
        raise NotImplementedError


class BaseImportCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--input-file",
            "-i",
            type=argparse.FileType("r", encoding="utf-8"),
            required=True,
        )
