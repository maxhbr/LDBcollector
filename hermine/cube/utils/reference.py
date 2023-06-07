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
    "allowed",
    "allowed_explanation",
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


@lru_cache(maxsize=None)
def get_ref_dict(model: str, natural_key):
    """Get a reference object from the shared database.

    :param model: A model content type name
    :param natural_key: A natural key
    :type natural_key: tuple
    :return: A dict of the reference object
    :rtype: dict
    """

    from cube.models import License, Generic

    model_class = {
        "license": License,
        "generic": Generic,
    }[model]

    try:
        return model_class.objects.get_by_natural_key(
            natural_key, using="shared"
        ).__dict__
    except model_class.DoesNotExist:
        return None


def license_reference_diff(lic) -> int:
    """Compare a license with the shared reference database.

    :param lic: A License object
    :return: 1 if license is different from reference, 0 if identical,
            -1 if license is not in the reference database
    """
    ref = get_ref_dict("license", lic.spdx_id)

    if ref is None:
        return -1

    return int(any(ref[key] != lic.__dict__[key] for key in LICENSE_SHARED_FIELDS))
