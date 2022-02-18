# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django import template

register = template.Library()


@register.filter
def getModifTriggerSet(value):
    """Takes an obligation_set from a generic obligation and returns its Mofication Trigger

    :param value: A generic.obligation_set
    :type value: list
    :raises ValueError:
    :return: a string in ['Altered', 'Unmodified', 'AlteredUnmodified']
    :rtype: string
    """
    modif_trigger_list = (obligation.trigger_mdf for obligation in value)
    if ("AlteredUnmodified" in modif_trigger_list) or (
        ("Altered" and "Unmodified") in modif_trigger_list
    ):
        return "Altered or Unmodified"
    elif "Altered" in modif_trigger_list:
        return "Altered"
    elif "Unmodified" in modif_trigger_list:
        return "Unmodified"
    else:
        raise ValueError("No modification trigger was given")


@register.filter
def getModifTriggerOblig(value):
    """Returns the Modification trigger of an Obligation object.

    :param value: A generic.obligation_set
    :type value: list
    :raises ValueError:
    :return: a string in ['Altered', 'Unmodified', 'AlteredUnmodified']
    :rtype: string
    """
    if value.trigger_mdf == "AlteredUnmodified":
        return "component is modified or not"
    elif value.trigger_mdf == "Altered":
        return "component is modified"
    elif value.trigger_mdf == "Unmodified":
        return "component is not modified"
    else:
        return "No modification trigger found"


@register.filter
def getExplTriggerOblig(value):
    if value.trigger_expl == "Distribution":
        return "source code or binaries are distributed "
    elif value.trigger_expl == "DistributionSource":
        return "source code is distributed"
    elif value.trigger_expl == "DistributionNonSource":
        return "binaries are distributed"
    elif value.trigger_expl == "NetworkAccess":
        return "component is accessible by network access"
    elif value.trigger_expl == "InternalUse":
        return "the component is used for internal usage"
    else:
        return "No modification trigger found"


@register.filter
def getColorTag(value):
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
