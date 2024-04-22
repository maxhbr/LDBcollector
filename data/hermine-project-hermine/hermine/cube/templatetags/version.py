# SPDX-FileCopyrightText: 2022 Louis Marie <louis.marie@orange.com>
# SPDX-License-Identifier: AGPL-3.0-only

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def version():
    return settings.VERSION
