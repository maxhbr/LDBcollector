# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
import logging
from typing import Iterable, TYPE_CHECKING

from django.core.serializers import serialize, deserialize
from django.db import transaction
from django.db.models import prefetch_related_objects

from cube.utils.importers import create_or_replace_by_natural_key

if TYPE_CHECKING:
    from cube.models import License


logger = logging.getLogger(__name__)


def check_licenses_against_policy(release):
    from cube.models import License, Derogation

    response = {}
    usages_lic_never_allowed = set()
    usages_lic_context_allowed = set()
    usages_lic_unknown = set()
    involved_lic = set()
    derogations = set()

    usages = release.usage_set.all()

    prefetch_related_objects(usages, "licenses_chosen")

    for usage in usages:
        for license in usage.licenses_chosen.all():
            involved_lic.add(license)

            if license.allowed == License.ALLOWED_ALWAYS:
                continue

            license_derogations = Derogation.objects.for_usage(usage).filter(
                license=license
            )
            if license_derogations.exists():
                for derogation in license_derogations:
                    derogations.add(derogation)
                continue

            if license.allowed == License.ALLOWED_NEVER:
                usages_lic_never_allowed.add(usage)
            elif license.allowed == License.ALLOWED_CONTEXT:
                usages_lic_context_allowed.add(usage)
            elif not license.allowed:
                usages_lic_unknown.add(usage)

    response["usages_lic_never_allowed"] = usages_lic_never_allowed
    response["usages_lic_context_allowed"] = usages_lic_context_allowed
    response["usages_lic_unknown"] = usages_lic_unknown
    response["involved_lic"] = involved_lic
    response["derogations"] = derogations

    return response


def get_license_triggered_obligations(
    license: "License", exploitation: str = None, modification: str = None
):
    """
    Get triggered obligations for a license and a usage context
    (if the component has been modified and how it's being distributed)

    :param license: A License instance
    :param exploitation: A value from Usage.EXPLOITATION_CHOICES
    :param modification: A value from Usage.MODIFICATION_CHOICES
    :return: A queryset or list of Obligation instances
    """
    obligations = license.obligation_set.all()

    # Do not use filter() here, so we can use the same queryset for both and benefit from prefetching
    if modification is not None:
        obligations = [
            o
            for o in obligations
            if ((o.trigger_mdf in modification) or (modification in o.trigger_mdf))
        ]

    if exploitation is not None:
        obligations = [
            o
            for o in obligations
            if (
                (o.trigger_expl in exploitation)
                or (exploitation in o.trigger_expl)
                or (o.passivity == "Passive")
            )  # Poor man bitwise OR
        ]

    return obligations


def get_licenses_triggered_obligations(
    licenses: Iterable["License"], exploitation: str = None, modification: str = None
):
    from cube.models import Obligation

    obligations_pk = set()
    for license in licenses:
        obligations_pk.update(
            o.pk
            for o in get_license_triggered_obligations(
                license, exploitation, modification
            )
        )
    return Obligation.objects.filter(pk__in=obligations_pk)


def get_usages_obligations(usages):
    """
    Get triggered obligations for a list of usages.

    :param usages: An iterable of Usage objects
    :return: A tuple with a list of generics, a list of licenses which
    obligations have no generics and the sorted list of licenses involved
    """
    generics_involved = set()
    specific_obligations = set()
    licenses_involved_set = set()

    # For performances, we prefetch all the related objects
    prefetch_related_objects(
        usages,
        "licenses_chosen",
        "licenses_chosen__obligation_set",
        "licenses_chosen__obligation_set__generic",
    )

    for usage in usages:
        for license in usage.licenses_chosen.all():
            licenses_involved_set.add(license)
            for obligation in get_license_triggered_obligations(
                license, usage.exploitation, usage.component_modified
            ):
                if obligation.generic:
                    generics_involved.add(obligation.generic)
                else:
                    specific_obligations.add(obligation)
    licenses_involved = sorted(licenses_involved_set, key=lambda x: x.spdx_id)
    return generics_involved, specific_obligations, licenses_involved


def get_generic_usages(usages, generic):
    """
    Filters a list of usages to retain only those triggering the provided
    generic obligation.
    :param usages: An iterable of Usage objects
    :param generic: A Generic object
    :return: An iterable of Usage objects that actually trigger the generic obligation
    """
    triggering_usages = set()

    for usage in usages:
        for license in usage.licenses_chosen.all():
            for obligation in get_license_triggered_obligations(
                license, usage.exploitation, usage.component_modified
            ):
                if obligation.generic and obligation.generic == generic:
                    triggering_usages.add(usage)

    return triggering_usages


def export_licenses(indent=False):
    from cube.models import Obligation, License

    return serialize(
        "json",
        list(License.objects.all()) + list(Obligation.objects.all()),
        indent=4 if indent else None,
        use_natural_foreign_keys=True,
        use_natural_primary_keys=True,
    )


@transaction.atomic()
def handle_licenses_json(data):
    created, updated = 0, 0
    for license_or_obligation in deserialize(
        "json", data, handle_forward_references=True
    ):
        from cube.models import Generic

        if len(license_or_obligation.deferred_fields) > 0:
            name = license_or_obligation.deferred_fields[
                list(license_or_obligation.deferred_fields.keys())[0]
            ][0]
            Generic.objects.get_or_create(name=name)

        if create_or_replace_by_natural_key(license_or_obligation):
            created += 1
        else:
            updated += 1

    logger.info(f"Licenses : {created} created / {updated} updated")
