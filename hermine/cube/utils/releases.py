#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.db.models import Q, F

from cube.models import Release, License, LicenseChoice, Version
from cube.utils.licenses import (
    get_licenses_to_check_or_create,
    check_licenses_against_policy,
    explode_SPDX_to_units,
)


def validate_step_1(release):
    """
    Looking for licenses that haven't been normalized, that is to say the ones
    that do not have a name fitting SPDX standards or that do not have been
    manually corrected.
    """
    context = dict()
    unnormalized_usages = release.usage_set.all().filter(
        version__spdx_valid_license_expr="", version__corrected_license=""
    )
    context["unormalized_usages"] = unnormalized_usages
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


def validate_step_3(release):
    """
    Confirm ANDs operators in SPDX expressions are not poorly registered ORs.
    """
    context = dict()
    response = confirm_ands(release.id)
    context["to_confirm"] = response["to_confirm"]
    context["confirmed"] = response["confirmed"]
    context["corrected"] = response["corrected"]

    return (len(response["to_confirm"]) == 0), context


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

    step_4_valid = (
        len(r["usages_lic_red"]) == 0
        and len(r["usages_lic_orange"]) == 0
        and len(r["usages_lic_grey"]) == 0
    )

    context["usages_lic_red"] = r["usages_lic_red"]
    context["usages_lic_orange"] = r["usages_lic_orange"]
    context["usages_lic_grey"] = r["usages_lic_grey"]
    context["step_4_valid"] = step_4_valid
    context["involved_lic"] = r["involved_lic"]
    context["derogations"] = r["derogations"]

    return step_4_valid, context


def update_validation_step(release: Release):
    info = dict()
    validation_step = 1

    step1, context = validate_step_1(release)
    info.update(context)
    if step1:
        validation_step = 2

    step2, context = validate_step_2(release)
    info.update(context)
    if step2:
        validation_step = 3

    step3, context = validate_step_3(release)
    info.update(context)
    if step3:
        validation_step = 4

    step4, context = validate_step_4(release)
    info.update(context)
    if step3:
        validation_step = 5

    step5, context = validate_step_5(release)
    if len(context["usages_lic_grey"]) > 0 and validation_step > 2:
        validation_step = 2
    info.update(context)
    if step5:
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
        unique_lic_ids = explode_SPDX_to_units(effective_license)
        if len(unique_lic_ids) == 1:
            try:
                unique_license = License.objects.get(spdx_id__exact=unique_lic_ids[0])
                usage.licenses_chosen.set(set([unique_license]))
                usage.license_expression = unique_lic_ids[0]
                usage.save()
            except License.DoesNotExist:
                print("Can't choose an unknown license", unique_lic_ids[0])
        else:
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
                for uniq_lic_id in set(explode_SPDX_to_units(expression_outs[0])):
                    unique_license = License.objects.get(spdx_id__exact=uniq_lic_id)
                    lic_to_add.add(unique_license)

                usage.licenses_chosen.set(lic_to_add)
                usage.save()
                resolved.add(usage)
            else:
                to_resolve.add(usage)

    response = {"to_resolve": to_resolve, "resolved": resolved}
    return response


def confirm_ands(release_id):
    """
    Because of unreliable metadata, many "Licence1 AND Licence2" expressions
    actually meant to be "Licence1 AND Licence2". That's why any expression of
    this type has to be manually validated.

    Args:

        release_id (int): The intern identifier of the concerned release

    Returns:
        response: A python object that has three fields :
            `to_confirm` the set of versions that needs an explicit confirmation
            `confirmed` the set of version whose AND has been confirmed
            `corrected` the set of version whose AND has been corrected
    """

    release = Release.objects.get(pk=release_id)

    to_confirm = set()
    confirmed = set()
    corrected = set()

    # TODO we should take into account cases like "(MIT OR ISC)AND Apache-3.0)"
    # with no space before the "AND"
    to_confirm = (
        Version.objects.filter(usage__release_id=release_id)
        .filter(spdx_valid_license_expr__contains=" AND ")
        .filter(Q(corrected_license="") | Q(corrected_license=None))
    )
    confirmed = (
        Version.objects.filter(usage__release_id=release_id)
        .filter(spdx_valid_license_expr__contains=" AND ")
        .filter(Q(corrected_license=F("spdx_valid_license_expr")))
    )
    corrected = (
        Version.objects.filter(usage__release_id=release_id)
        .filter(spdx_valid_license_expr__contains=" AND ")
        .exclude(
            Q(corrected_license=F("spdx_valid_license_expr"))
            | Q(corrected_license="")
            | Q(corrected_license=None)
        )
    )
    response = {
        "to_confirm": to_confirm,
        "confirmed": confirmed,
        "corrected": corrected,
    }
    return response
