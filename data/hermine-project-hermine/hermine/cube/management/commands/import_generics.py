#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from cube.management.commands._base_commands import BaseImportCommand
from cube.utils.generics import handle_generics_json


class Command(BaseImportCommand):
    def handle(self, *args, input_file, **options):
        handle_generics_json(input_file.read())
