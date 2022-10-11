# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django import template

from cube.models import License

register = template.Library()


@register.filter
def licenseAllowedCSS(license: License):
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


@register.filter
def licenseReviewCSS(license: License):
    """Returns the appropriated bulma CSS class according to license review.

    :param license: A License object
    :type license: License
    :return: A CSS string
    :rtype string
    """
    if license.status == License.STATUS_CHECKED:
        return "is-success"
    if license.status == License.STATUS_PENDING:
        return "is-warning"
    if license.status == License.STATUS_TO_DISCUSS:
        return "is-danger"
    return "is-dark"


@register.filter
def licenseCopyleftCSS(license: License):
    """Returns the appropriated bulma CSS class according to license copyleft.

    :param license: A License object
    :type license: License
    :return: A CSS string
    :rtype string
    """
    if license.copyleft == License.COPYLEFT_NONE:
        return "is-success"
    if license.copyleft == License.COPYLEFT_WEAK:
        return "is-warning"
    if (
        license.copyleft == License.COPYLEFT_STRONG
        or license.copyleft == License.COPYLEFT_NETWORK
        or license.copyleft == License.COPYLEFT_NETWORK_WEAK
    ):
        return "is-danger"
    return "is-dark"


@register.filter
def licenseFOSSCSS(license: License):
    """Returns the appropriated bulma CSS class according to license foss.

    :param license: A License object
    :type license: License
    :return: A CSS string
    :rtype string
    """
    if license.foss == License.FOSS_YES or license.foss == License.FOSS_YES_AUTO:
        return "is-success"
    if license.foss == License.FOSS_NO or license.foss == License.FOSS_NO_AUTO:
        return "is-warning"
    return "is-danger"
