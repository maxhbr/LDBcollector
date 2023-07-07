#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from functools import lru_cache
from django.db.models import F

LICENSE_SHARED_FIELDS = (
    "spdx_id",
    "long_name",
    "license_version",
    "radical",
    "autoupgrade",
    "steward",
    "inspiration_spdx",
    "copyleft",
    "url",
    "osi_approved",
    "fsf_approved",
    "foss",
    "patent_grant",
    "ethical_clause",
    "non_commercial",
    "non_tivoisation",
    "law_choice",
    "comment",
    "verbatim",
)

OBLIGATION_SHARED_FIELDS = (
    "name",
    "verbatim",
    "passivity",
    "trigger_expl",
    "trigger_mdf",
    # treat generic.name as a special case
)


GENERIC_SHARED_FIELDS = ("name", "description", "metacategory", "passivity")


@lru_cache(maxsize=None)
def get_license_ref_dict(spdx_id):
    """Get a license reference object from the shared database.

    :param spdx_id: A SPDX license identifier
    :type spdx_id: str
    :return: A dict of the reference object and related objects
    :rtype: dict
    """
    from cube.models import License, Obligation

    try:
        ref = (
            License.objects.values(*LICENSE_SHARED_FIELDS)
            .using("shared")
            .get(spdx_id=spdx_id)
        )
    except License.DoesNotExist:
        return None

    ref["obligations"] = list(
        Obligation.objects.using("shared")
        .filter(license__spdx_id=spdx_id)
        .values("generic__name", *OBLIGATION_SHARED_FIELDS)
    )
    return ref


def license_reference_diff(lic) -> int:
    """Compare a license with the shared reference database.

    For performances reasons :
    * expect obligation_count to be set on the license
    object and not to be computed from the database.
    * expect obligation_set to be prefetched on the license object.

    :param lic: A License object
    :return: 1 if license is different from reference, 0 if identical,
            -1 if license is not in the reference database
    """
    ref = get_license_ref_dict(lic.spdx_id)

    if ref is None:
        return -1

    # Compare license fields
    if any(ref[key] != lic.__dict__[key] for key in LICENSE_SHARED_FIELDS):
        return 1

    # Compare obligations count
    obligation_count = (
        lic.obligation_count
        if hasattr(lic, "obligation_count")
        else lic.obligation_set.all().count()
    )
    if len(ref["obligations"]) != obligation_count:
        return 1

    # Compare obligations
    for obligation in lic.obligation_set.all():
        # Find the corresponding obligation in the reference
        ref_obligation = next(
            (
                ref_ob
                for ref_ob in ref["obligations"]
                if ref_ob["name"] == obligation.name
            ),
            None,
        )

        if ref_obligation is None:
            return 1

        obligation_dict = obligation.__dict__
        obligation_dict["generic__name"] = (
            obligation.generic and obligation.generic.name
        )

        if any(
            obligation_dict[key] != ref_obligation[key]
            for key in ["generic__name", *OBLIGATION_SHARED_FIELDS]
        ):
            return 1

    return 0


@lru_cache(maxsize=None)
def get_generic_ref_dict(name):
    """Get a generic reference object from the shared database.

    :param name: A generic name
    :type name: str
    :return: A dict of the reference object and related objects
    :rtype: dict
    """
    from cube.models import Generic

    try:
        ref = (
            Generic.objects.values(*GENERIC_SHARED_FIELDS)
            .using("shared")
            .get(name=name)
        )
    except Generic.DoesNotExist:
        return None

    return ref


def generic_reference_diff(gen) -> int:
    """Compare a generic with the shared reference database.

    :param gen: A Generic object
    :return: 1 if generic is different from reference, 0 if identical,
            -1 if generic is not in the reference database
    """
    ref = get_generic_ref_dict(gen.name)

    if ref is None:
        return -1

    if any(ref[key] != gen.__dict__[key] for key in GENERIC_SHARED_FIELDS):
        return 1

    return 0


def join_obligations(local, ref):
    """
    Outer join obligations with same name

    :type local: cube.models.License
    :type ref: cube.models.License
    """
    obligations_pairs = []
    ref_obligations = list(
        ref.obligation_set.annotate(generic__name=F("generic__name")).all()
    )

    for obligation in local.obligation_set.annotate(
        generic__name=F("generic__name")
    ).all():
        ref_index = next(
            (
                i
                for i, ref_obligation in enumerate(ref_obligations)
                if ref_obligation.name == obligation.name
            ),
            None,
        )
        ref = ref_obligations.pop(ref_index) if ref_index is not None else None
        obligations_pairs.append((obligation, ref))

    for ref_obligation in ref_obligations:
        obligations_pairs.append((None, ref_obligation))

    return obligations_pairs
