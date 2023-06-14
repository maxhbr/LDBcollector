#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from functools import lru_cache

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
    "generic__name",
    "name",
    "verbatim",
    "passivity",
    "trigger_expl",
    "trigger_mdf",
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
        .values(*OBLIGATION_SHARED_FIELDS)
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

    if any(ref[key] != lic.__dict__[key] for key in LICENSE_SHARED_FIELDS):
        return 1

    obligation_count = (
        lic.obligation_count
        if hasattr(lic, "obligation_count")
        else lic.obligation_set.all().count()
    )
    if len(ref["obligations"]) != obligation_count:
        return 1

    for obligation in lic.obligation_set.all():
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
            for key in OBLIGATION_SHARED_FIELDS
        ):
            return 1

    return 0
