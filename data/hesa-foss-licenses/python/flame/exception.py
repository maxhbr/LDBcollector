# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

class FlameException(Exception):
    """
    Simple exception for module
    """
    def __init__(self, message, problems=None):
        super().__init__(message)
        self._problems = problems

    def problems(self):
        if self._problems:
            return self._problems
        else:
            return ''
