# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django import template

from cube.models import License

register = template.Library()


@register.filter
def getColorTag(value: License):
    """Returns the appropriated css tag according to the color of the license.


    :param value: A License object
    :type value: License
    :return: A CSS string
    :rtype: string
    """
    if value.color == "Green":
        return "is-success"
    elif value.color == "Orange":
        return "is-warning"
    elif value.color == "Red":
        return "is-danger"
    else:
        return "is-dark"
