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


def update_validation_step(release):
    info = dict()
    validation_step = 1

    # ==== Step 1 ====
    # Looking for licenses that haven't been normalized, that is to say the ones
    # that do not have a name fitting SPDX standards or that do not have been
    # manually corrected.
    unnormalized_usages = release.usage_set.all().filter(
        version__spdx_valid_license_expr="", version__corrected_license=""
    )
    nb_validated_components = len(release.usage_set.all()) - len(unnormalized_usages)
    if len(unnormalized_usages) == 0:
        validation_step = 2

    info["unnormalized_usages"] = unnormalized_usages
    info["nb_validated_components"] = nb_validated_components

    # ==== Step 2 ===
    licenses = get_licenses_to_check_or_create(release)

    info["licenses_to_check"] = licenses["licenses_to_check"]
    info["licenses_to_create"] = licenses["licenses_to_create"]
    if (
        len(info["licenses_to_check"]) == 0
        and len(info["licenses_to_create"]) == 0
        and validation_step == 2
    ):
        validation_step = 3
    # ==== Step 2 bis ===
    response = confirm_ands(release.id)
    info["to_confirm"] = response["to_confirm"]
    info["confirmed"] = response["confirmed"]
    info["corrected"] = response["corrected"]

    if len(response["to_confirm"]) == 0 and validation_step == 3:
        validation_step = 4

    # ==== For step 3 ====
    response = propagate_choices(release.id)
    info["to_resolve"] = response["to_resolve"]
    info["resolved"] = response["resolved"]

    if len(response["to_resolve"]) == 0 and validation_step == 4:
        validation_step = 5

    # ==== For step 4 ====
    r = check_licenses_against_policy(release)

    if len(r["usages_lic_grey"]) > 0 and validation_step > 2:
        validation_step = 2

    if (
        len(r["usages_lic_red"]) == 0
        and len(r["usages_lic_orange"]) == 0
        and len(r["usages_lic_grey"]) == 0
    ):
        step_4_valid = True
    else:
        step_4_valid = False

    if step_4_valid and validation_step == 5:
        validation_step = 6

    info["usages_lic_red"] = r["usages_lic_red"]
    info["usages_lic_orange"] = r["usages_lic_orange"]
    info["usages_lic_grey"] = r["usages_lic_grey"]
    info["step_4_valid"] = step_4_valid
    info["involved_lic"] = r["involved_lic"]
    info["derogations"] = r["derogations"]

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
