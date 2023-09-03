# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

class FlameException(Exception):
    """
    Simple exception for module
    """
    def __init__(self, message):
        super().__init__(message)
