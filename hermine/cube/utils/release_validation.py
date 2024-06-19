#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import logging
from itertools import groupby

from django.db.models import (
    Count,
    Case,
    When,
    F,
    Subquery,
    OuterRef,
    Q,
)

from cube.models import (
    Release,
    License,
    LicenseChoice,
    LicenseCuration,
    Exploitation,
    Derogation,
)
from cube.utils.spdx import has_ors, is_ambiguous, simplified

logger = logging.getLogger(__name__)


STEP_CURATION = 1
STEP_CONFIRM_AND = 2
STEP_EXPLOITATIONS = 3
STEP_CHOICES = 4
STEP_POLICY = 5


# Functions with side effect to update releases according to curations and choices
def apply_curations(release):
    usages = (
        release.usage_set.filter(version__corrected_license="").annotate(
            imported_license=Case(
                When(
                    version__spdx_valid_license_expr="",
                    then=F("version__declared_license_expr"),
                ),
                default=F("version__spdx_valid_license_expr"),
            )
        )
        # includes curations with semantic versioning which may not match
        # but still a big performance boost to skip usages with no curations later
        .annotate(
            curation=Subquery(
                LicenseCuration.objects.filter(
                    Q(component=OuterRef("version__component")) | Q(component=None),
                    Q(version=OuterRef("version")) | Q(version=None),
                    Q(expression_in=OuterRef("imported_license")),
                ).values("expression_out")[:1]
            )  # includes curations with semantic versioning
        )
    )

    for usage in usages:
        if usage.curation is not None:
            # Check there are no conflicting curations (subquery returns only first row)
            try:
                curation = LicenseCuration.objects.for_version(usage.version).get()
                usage.version.corrected_license = curation.expression_out
                usage.version.save()
            except (
                LicenseCuration.DoesNotExist,
                LicenseCuration.MultipleObjectsReturned,
            ):
                logger.warning("Multiple curations for %s", usage.version.component)


def propagate_choices(release: Release):
    """
    Transfer license information from component to usage.
    Set usage.license_expression if there is no ambiguity.

    :param release: Release to update
    :return: dict with two keys: to_resolve and resolved containing the corresponding usages
    """
    to_resolve = set()

    usages = (
        release.usage_set.filter(license_expression="")
        .select_related("version", "version__component", "release", "release__product")
        .prefetch_related("licenses_chosen")
        # includes choices with semantic versioning which may not match
        # but still a big performance boost to skip usage with no derogation later
        .annotate(
            licensechoice=Subquery(
                LicenseChoice.objects.filter(
                    Q(component=OuterRef("version__component")) | Q(component=None),
                    Q(version=OuterRef("version")) | Q(version=None),
                    Q(product=OuterRef("release__product")) | Q(product=None),
                    Q(release=OuterRef("release")) | Q(release=None),
                    Q(category__in=OuterRef("release__product__categories"))
                    | Q(category=None),
                    Q(scope=OuterRef("scope")) | Q(scope=""),
                    Q(exploitation=OuterRef("exploitation")) | Q(exploitation=""),
                ).values("pk")[:1]
            )
        )
    )

    for usage in usages:
        if usage.version.license_is_ambiguous:
            continue

        if not has_ors(usage.version.effective_license):
            try:
                usage.license_expression = usage.version.effective_license
                usage.save()
            except License.DoesNotExist:
                logger.warning(
                    "%s : can not choose unknown license",
                    usage.version.component,
                )
            continue

        if not usage.license_expression:  # do not override already made choices
            if usage.licensechoice is None:
                to_resolve.add(usage)
                continue

            try:
                expression_out = (
                    LicenseChoice.objects.for_usage(usage)
                    .values_list("expression_out", flat=True)
                    .get()
                )
            except (LicenseChoice.DoesNotExist, LicenseChoice.MultipleObjectsReturned):
                to_resolve.add(usage)
            else:
                usage.license_expression = expression_out
                usage.save()

    resolved = (
        usage
        for usage in release.usage_set.all()
        .select_related("version")
        .exclude(license_expression="")
        if has_ors(
            usage.version.effective_license
        )  # we want to list only usages for which a choice was actually necessary
    )

    return {"to_resolve": to_resolve, "resolved": resolved}


def check_licenses_against_policy(release: Release):
    usages_lic_never_allowed = set()
    usages_lic_context_allowed = set()
    usages_lic_unknown = set()
    involved_lic = set()
    derogations = set()

    usages = (
        release.usage_set.exclude(licenses_chosen=None)
        .select_related("version", "version__component", "release", "release__product")
        .prefetch_related("licenses_chosen")
        # includes derogations with semantic versioning which may not match
        # but still a big performance boost to skip usage with no derogation later
        .annotate(
            derogation=Subquery(
                Derogation.objects.filter(
                    Q(component=OuterRef("version__component")) | Q(component=None),
                    Q(version=OuterRef("version")) | Q(version=None),
                    Q(product=OuterRef("release__product")) | Q(product=None),
                    Q(release=OuterRef("release")) | Q(release=None),
                    Q(category__in=OuterRef("release__product__categories"))
                    | Q(category=None),
                    Q(scope=OuterRef("scope")) | Q(scope=""),
                    Q(exploitation=OuterRef("exploitation")) | Q(exploitation=""),
                    Q(license__in=OuterRef("licenses_chosen")),
                    Q(linking=OuterRef("linking")) | Q(linking=""),
                    Q(modification=OuterRef("component_modified")) | Q(modification=""),
                ).values("pk")[:1]
            )
        )
    )

    # Because of the way sql JOIN query operates, usages are duplicated
    # for each license_chosen or categories. They are all identical objets,
    # except some have a derogation and some don't.
    for pk, usages in groupby(usages, key=lambda u: u.id):
        usages = list(usages)
        usage = usages[0]
        for license in usage.licenses_chosen.all():
            involved_lic.add(license)

            if license.allowed == License.ALLOWED_ALWAYS:
                continue

            if any(u.derogation is not None for u in usages):
                license_derogations = list(
                    Derogation.objects.for_usage(usage).filter(license=license)
                )
                if len(license_derogations):
                    for derogation in license_derogations:
                        derogations.add(derogation)
                    continue

            if license.allowed == License.ALLOWED_NEVER:
                usages_lic_never_allowed.add(usage)
            elif license.allowed == License.ALLOWED_CONTEXT:
                usages_lic_context_allowed.add(usage)
            elif not license.allowed:
                usages_lic_unknown.add(usage)

    return {
        "usages_lic_never_allowed": usages_lic_never_allowed,
        "usages_lic_context_allowed": usages_lic_context_allowed,
        "usages_lic_unknown": usages_lic_unknown,
        "involved_lic": involved_lic,
        "derogations": derogations,
    }


# Validations step methods
def validate_expressions(release):
    """
    Check for components versions that do not have valid SPDX license expressions.
    """
    context = dict()
    invalid_expressions = release.usage_set.filter(
        version__spdx_valid_license_expr="", version__corrected_license=""
    )
    context["invalid_expressions"] = invalid_expressions

    context["fixed_expressions"] = release.usage_set.filter(
        version__spdx_valid_license_expr=""
    ).exclude(version__corrected_license="")

    context["nb_validated_components"] = len(release.usage_set.all()) - len(
        invalid_expressions
    )

    return len(invalid_expressions) == 0, context


def validate_ands(release: Release):
    """
    Confirm that ANDs operators in SPDX expressions are not poorly registered ORs.
    """
    context = dict()
    ambiguous_spdx = [
        usage
        for usage in release.usage_set.exclude(
            version__spdx_valid_license_expr=""
        ).select_related("version")
        if is_ambiguous(usage.version.spdx_valid_license_expr)
    ]

    context["to_confirm"] = [
        u for u in ambiguous_spdx if u.version.corrected_license == ""
    ]
    context["confirmed"] = [
        u.version
        for u in ambiguous_spdx
        if u.version.corrected_license == u.version.spdx_valid_license_expr
        or u.version.corrected_license == simplified(u.version.spdx_valid_license_expr)
    ]
    context["corrected"] = [
        u.version
        for u in ambiguous_spdx
        if u.version.corrected_license
        and u.version.corrected_license != u.version.spdx_valid_license_expr
        and u.version.corrected_license != simplified(u.version.spdx_valid_license_expr)
    ]

    return (len(context["to_confirm"]) == 0), context


def validate_exploitations(release: Release):
    """
    Check all scopes have a defined exploitation
    """
    context = dict()
    unset_scopes = set()
    scopes = (
        release.usage_set.filter(exploitation="")
        .order_by("scope")
        .values_list("project", "scope")
        .annotate(Count("id"))
    )

    for project, scope, count in scopes:
        try:
            release.exploitations.get(
                (Q(scope=scope) | Q(scope="")) & (Q(project=project) | Q(project=""))
            )
        except Exploitation.DoesNotExist:
            unset_scopes.add((project, scope, count))
        except Exploitation.MultipleObjectsReturned:
            logger.warning("Multiple exploitations for %s %s", project, scope)
            unset_scopes.add((project, scope, count))

    context["exploitations"] = release.exploitations.all()
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


# Apply all rules and check validation steps
def update_validation_step(release: Release):
    info = dict()
    validation_step = 0

    apply_curations(release)

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
