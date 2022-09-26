# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django import template

from cube.models import License

register = template.Library()


@register.filter
def licenseCSS(license: License):
    """Returns the appropriated bulma CSS class according to license policy.

    :param license: A License object
    :type license: License
    :return: A CSS string
    :rtype: string
    """
    if license.allowed == License.ALLOWED_ALWAYS:
        return "is-success"
    elif license.allowed == License.ALLOWED_CONTEXT:
        return "is-warning"
    elif license.allowed == License.ALLOWED_NEVER:
        return "is-danger"
    else:
        return "is-dark"
