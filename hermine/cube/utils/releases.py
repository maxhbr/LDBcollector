#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import logging

from django.db.models import F, Count

from cube.models import (
    Release,
    License,
    LicenseChoice,
    ExpressionValidation,
    LicenseCuration,
    Exploitation,
)
from cube.utils.licenses import (
    check_licenses_against_policy,
    explode_spdx_to_units,
    is_ambiguous,
    has_ors,
)

logger = logging.getLogger(__name__)


STEP_CURATION = 1
STEP_CONFIRM_AND = 2
STEP_EXPLOITATIONS = 3
STEP_CHOICES = 4
STEP_POLICY = 5


def validate_expressions(release):
    """
    Check for components versions that do not have valid SPDX license expressions.
    """
    context = dict()
    invalid_expressions = release.usage_set.filter(
        version__spdx_valid_license_expr="",
        version__corrected_license="",
    )

    for usage in invalid_expressions:
        try:
            usage.version.spdx_valid_license_expr = (
                LicenseCuration.objects.for_usage(usage)
                .get(expression_in=usage.version.declared_license_expr)
                .expression_out
            )
            usage.version.save()
        except LicenseCuration.DoesNotExist:
            continue

    invalid_expressions = [
        usage
        for usage in invalid_expressions
        if not usage.version.spdx_valid_license_expr
    ]
    context["invalid_expressions"] = invalid_expressions

    context["fixed_expressions"] = release.usage_set.exclude(
        version__corrected_license=""
    ).exclude(version__spdx_valid_license_expr=F("version__corrected_license"))

    context["nb_validated_components"] = len(release.usage_set.all()) - len(
        invalid_expressions
    )

    return len(invalid_expressions) == 0, context


def validate_ands(release: Release):
    """
    Confirm ANDs operators in SPDX expressions are not poorly registered ORs.
    """
    context = dict()
    ambiguous_spdx = [
        usage
        for usage in release.usage_set.all()
        if is_ambiguous(usage.version.spdx_valid_license_expr)
    ]

    for usage in ambiguous_spdx:
        try:
            usage.version.corrected_license = (
                ExpressionValidation.objects.for_usage(usage)
                .filter(expression_in=usage.version.spdx_valid_license_expr)
                .values_list("expression_out", flat=True)
                .get()
            )
            usage.version.save()
        except ExpressionValidation.DoesNotExist:
            continue

    context["to_confirm"] = [
        u for u in ambiguous_spdx if not u.version.corrected_license
    ]
    context["confirmed"] = [
        u.version
        for u in ambiguous_spdx
        if u.version.corrected_license == u.version.spdx_valid_license_expr
    ]
    context["corrected"] = [
        u.version
        for u in ambiguous_spdx
        if u.version.corrected_license
        and u.version.corrected_license != u.version.spdx_valid_license_expr
    ]

    return (len(context["to_confirm"]) == 0), context


def validate_exploitations(release: Release):
    """
    Check all scopes have a defined exploitation
    """
    context = dict()
    scope_exploitations = set()
    unset_scopes = set()
    scopes = (
        release.usage_set.all()
        .order_by("scope")
        .values_list("scope")
        .annotate(Count("id"))
    )
    for scope, count in scopes:
        try:
            exploitation = release.exploitations.get(scope=scope)
            scope_exploitations.add(exploitation)
        except Exploitation.DoesNotExist:
            unset_scopes.add(scope)

    context["exploitations"] = scope_exploitations
    context["unset_scopes"] = unset_scopes

    return len(unset_scopes) == 0, context


def validate_choices(release):
    """
    Check all licenses choices are done.
    """
    context = dict()
    response = propagate_choices(release)
    context["to_resolve"] = response["to_resolve"]
    context["resolved"] = response["resolved"]

    return len(response["to_resolve"]) == 0, context


def validate_policy(release):
    """
    Check that the licenses are compatible with policy.
    """
    context = dict()
    r = check_licenses_against_policy(release)

    step_5_valid = (
        len(r["usages_lic_never_allowed"]) == 0
        and len(r["usages_lic_context_allowed"]) == 0
        and len(r["usages_lic_unknown"]) == 0
    )

    context["usages_lic_never_allowed"] = r["usages_lic_never_allowed"]
    context["usages_lic_context_allowed"] = r["usages_lic_context_allowed"]
    context["usages_lic_unknown"] = r["usages_lic_unknown"]
    context["involved_lic"] = r["involved_lic"]
    context["derogations"] = r["derogations"]

    return step_5_valid, context


def update_validation_step(release: Release):
    info = dict()
    validation_step = 0

    step1, context = validate_expressions(release)
    info.update(context)
    if step1:
        validation_step = 1

    step2, context = validate_ands(release)
    info.update(context)
    if step2 and validation_step == 1:
        validation_step = 2

    step3, context = validate_exploitations(release)
    info.update(context)
    if step3 and validation_step == 2:
        validation_step = 3

    step4, context = validate_choices(release)
    info.update(context)
    if step4 and validation_step == 3:
        validation_step = 4

    step5, context = validate_policy(release)
    info.update(context)
    if step5 and validation_step == 4:
        validation_step = 5

    release.valid_step = validation_step
    release.save()

    return info


def propagate_choices(release: Release):
    """
    Transfer license information from component to usage. Set usage.license_chosen if
    there is no ambiguity.

    Args:
        release (int): The intern identifier of the concerned release

    Returns:
        response: A python object that has two field :
            `to_resolve` the set of usages which needs an explicit choice
            `resolved` the set of usages for which a choice has been made
    """

    resolved = {
        usage
        for usage in release.usage_set.all()
        .select_related("version", "version__component")
        .prefetch_related("licenses_chosen")
        .exclude(license_expression="")
        if has_ors(
            usage.version.effective_license
        )  # we want to list only usages for which a choice was actually necessary
    }

    to_resolve = set()

    for usage in release.usage_set.all().filter(license_expression=""):
        if usage.version.license_is_ambiguous:
            continue

        if not has_ors(usage.version.effective_license):
            licenses_spdx_ids = explode_spdx_to_units(usage.version.effective_license)

            try:
                licenses = [
                    License.objects.get(spdx_id=spdx_id)
                    for spdx_id in licenses_spdx_ids
                ]
                usage.licenses_chosen.set(licenses)
                usage.license_expression = usage.version.effective_license
                usage.save()
            except License.DoesNotExist:
                logger.warning(
                    "%s : can not choose unknown license",
                    usage.version.component,
                )
        else:
            expression_outs = LicenseChoice.objects.for_usage(usage).values_list(
                "expression_out", flat=True
            )
            if len(set(expression_outs)) == 1:
                usage.license_expression = expression_outs[0]
                licenses = [
                    License.objects.get(spdx_id=spdx_id)
                    for spdx_id in set(explode_spdx_to_units(expression_outs[0]))
                ]
                usage.licenses_chosen.set(licenses)
                usage.save()
                resolved.add(usage)
            else:
                to_resolve.add(usage)

    response = {"to_resolve": to_resolve, "resolved": resolved}
    return response
