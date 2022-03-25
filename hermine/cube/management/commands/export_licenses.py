#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from cube.management.commands._base_commands import BaseExportCommand
from cube.utils.licenses import export_licenses


class Command(BaseExportCommand):
    help = "Export licenses to JSON"

    def get_data(self):
        return export_licenses(indent=self.beautify)
