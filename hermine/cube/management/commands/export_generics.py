#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from cube.management.commands._base_commands import BaseExportCommand
from cube.utils.generics import export_generics


class Command(BaseExportCommand):
    def get_data(self):
        return export_generics(indent=self.beautify)
