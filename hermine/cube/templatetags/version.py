# SPDX-FileCopyrightText: 2022 Louis Marie <louis.marie@orange.com>
# SPDX-License-Identifier: AGPL-3.0-only

from django import template
import time
import os
from django.conf import settings

register = template.Library()


@register.simple_tag
def version_date():
    version_path = settings.VERSION_FILE_PATH
    if version_path:
        try:
            with open(version_path, "r") as file:
                data = file.read().rstrip()
                return data
        except FileNotFoundError:
            print("Version file not found at ", version_path)
    return ""
