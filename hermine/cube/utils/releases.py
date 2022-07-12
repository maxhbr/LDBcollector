#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import logging

from django.db.models import Q

from cube.models import Release, License, LicenseChoice
from cube.utils.licenses import (
    get_licenses_to_check_or_create,
    check_licenses_against_policy,
    explode_spdx_to_units,
    is_ambiguous,
)

logger = logging.getLogger(__name__)


def validate_step_1(release):
    """
    Check for licenses that haven't been normalized.
    """
    context = dict()
    unnormalized_usages = release.usage_set.all().filter(
        version__spdx_valid_license_expr="", version__corrected_license=""
    )
    context["unnormalized_usages"] = unnormalized_usages
    context["nb_validated_components"] = len(release.usage_set.all()) - len(
        unnormalized_usages
    )

    return len(unnormalized_usages) == 0, context


def validate_step_2(release):
    """
    Check that all the licences in a release have been created and checked.
    """
    context = dict()
    licenses = get_licenses_to_check_or_create(release)
    context["licenses_to_check"] = licenses["licenses_to_check"]
    context["licenses_to_create"] = licenses["licenses_to_create"]

    return (
        len(context["licenses_to_check"]) == 0
        and len(context["licenses_to_create"]) == 0
    ), context


def validate_step_3(release: Release):
    """
    Confirm ANDs operators in SPDX expressions are not poorly registered ORs.
    """
    context = dict()
    ambigious_spdx = [
        usage.version
        for usage in release.usage_set.all()
        if is_ambiguous(usage.version.spdx_valid_license_expr)
    ]
    context["to_confirm"] = [c for c in ambigious_spdx if not c.corrected_license]
    context["confirmed"] = [
        c for c in ambigious_spdx if c.corrected_license == c.spdx_valid_license_expr
    ]
    context["corrected"] = [
        c
        for c in ambigious_spdx
        if c.corrected_license and c.corrected_license != c.spdx_valid_license_expr
    ]

    return (len(context["to_confirm"]) == 0), context


def validate_step_4(release):
    """
    Check all licenses choices are done.
    """
    context = dict()
    response = propagate_choices(release.id)
    context["to_resolve"] = response["to_resolve"]
    context["resolved"] = response["resolved"]

    return len(response["to_resolve"]) == 0, context


def validate_step_5(release):
    """
    Check that the licences are compatible with policy.
    """
    context = dict()
    r = check_licenses_against_policy(release)

    step_5_valid = (
        len(r["usages_lic_red"]) == 0
        and len(r["usages_lic_orange"]) == 0
        and len(r["usages_lic_grey"]) == 0
    )

    context["usages_lic_red"] = r["usages_lic_red"]
    context["usages_lic_orange"] = r["usages_lic_orange"]
    context["usages_lic_grey"] = r["usages_lic_grey"]
    context["involved_lic"] = r["involved_lic"]
    context["derogations"] = r["derogations"]

    return step_5_valid, context


def update_validation_step(release: Release):
    info = dict()
    validation_step = 1

    step1, context = validate_step_1(release)
    info.update(context)
    if step1:
        validation_step = 2

    step2, context = validate_step_2(release)
    info.update(context)
    if step2 and validation_step == 2:
        validation_step = 3

    step3, context = validate_step_3(release)
    info.update(context)
    if step3 and validation_step == 3:
        validation_step = 4

    step4, context = validate_step_4(release)
    info.update(context)
    if step4 and validation_step == 4:
        validation_step = 5

    step5, context = validate_step_5(release)
    if len(context["usages_lic_grey"]) > 0 and validation_step > 2:
        validation_step = 2
    info.update(context)
    if step5 and validation_step == 5:
        validation_step = 6

    release.valid_step = validation_step
    release.save()

    return info


def propagate_choices(release_id):
    """
    Transfer license information from component to usage. Set usage.license_chosen if
    there is no ambiguity.

    Args:

        release_id (int): The intern identifier of the concerned release

    Returns:
        response: A python object that has two field :
            `to_resolve` the set of usages which needs an explicit choice
            `resolved` the set of usages for which a choice has just been made
    """

    release = Release.objects.get(pk=release_id)

    to_resolve = set()
    resolved = set()

    unchosen_usages = release.usage_set.all().filter(license_expression="")
    for usage in unchosen_usages:
        if usage.version.corrected_license:
            effective_license = usage.version.corrected_license
        else:
            effective_license = usage.version.spdx_valid_license_expr
        unique_lic_ids = explode_spdx_to_units(effective_license)
        chuncks = effective_license.replace("(", " ").replace(")", " ").upper().split()

        only_ands = (
            "OR" not in chuncks
        )  # imply is_ambiguous is True so we need corrected_license
        all_licenses_apply = only_ands and usage.version.corrected_license

        if len(unique_lic_ids) == 1 or all_licenses_apply:
            try:
                unique_licenses = set()
                for unique_lic_id in unique_lic_ids:
                    unique_license = License.objects.get(spdx_id__exact=unique_lic_id)
                    unique_licenses.add(unique_license)
                usage.licenses_chosen.set(unique_licenses)
                usage.license_expression = effective_license
                usage.save()
            except License.DoesNotExist:
                logger.warning(
                    "%s : can not choose unknown license %s",
                    usage.version.component,
                    unique_lic_ids[0],
                )
        elif usage.version.corrected_license or not is_ambiguous(effective_license):
            choices = LicenseChoice.objects.filter(
                Q(expression_in=effective_license),
                Q(component=usage.version.component) | Q(component=None),
                Q(version=usage.version) | Q(version=None),
                Q(product=usage.release.product) | Q(product=None),
                Q(release=usage.release) | Q(release=None),
                Q(scope=usage.scope) | Q(scope=None),
            )
            expression_outs = []
            for choice in choices:
                expression_outs.append(choice.expression_out)
            if len(set(expression_outs)) == 1:
                usage.license_expression = expression_outs[0]
                lic_to_add = set()
                for uniq_lic_id in set(explode_spdx_to_units(expression_outs[0])):
                    unique_license = License.objects.get(spdx_id__exact=uniq_lic_id)
                    lic_to_add.add(unique_license)

                usage.licenses_chosen.set(lic_to_add)
                usage.save()
                resolved.add(usage)
            else:
                to_resolve.add(usage)

    response = {"to_resolve": to_resolve, "resolved": resolved}
    return response
