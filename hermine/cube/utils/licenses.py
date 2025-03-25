# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
import io
import json
import logging
import re
import tarfile
import unicodedata
from typing import Iterable, TYPE_CHECKING

from django.core.serializers import serialize, deserialize
from django.db import transaction
from django.db.models import prefetch_related_objects

from cube.utils.importers import create_or_replace_by_natural_key
from cube.utils.reference import LICENSE_SHARED_FIELDS, GENERIC_SHARED_FIELDS

if TYPE_CHECKING:
    from cube.models import License

logger = logging.getLogger(__name__)


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
    compliance action.
    :param usages: An iterable of Usage objects
    :param generic: A Generic object
    :return: An iterable of Usage objects that actually trigger the compliance action
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
    from cube.models import Obligation, License, LicensePolicy, Generic

    return serialize(
        "json",
        list(Generic.objects.all())
        + list(License.objects.all())
        + list(Obligation.objects.all())
        + list(LicensePolicy.objects.all()),
        indent=4 if indent else None,
        use_natural_foreign_keys=True,
        use_natural_primary_keys=True,
    )


def export_shared_archive():
    from cube.models import License, Generic

    # Create a tar file with one json file per license
    with io.BytesIO() as tar_buffer:
        with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
            for license in License.objects.all():
                license_json = serialize(
                    "json",
                    [license],
                    use_natural_foreign_keys=True,
                    use_natural_primary_keys=True,
                )
                # Filter shared fields
                license_dict = json.loads(license_json)[0]
                license_dict = {
                    k: v
                    for k, v in license_dict["fields"].items()
                    if k in LICENSE_SHARED_FIELDS
                }

                obligation_json = serialize(
                    "json",
                    license.obligation_set.all(),
                    use_natural_foreign_keys=True,
                    use_natural_primary_keys=True,
                    indent=4,
                )
                license_dict["obligations"] = [
                    o["fields"] for o in json.loads(obligation_json)
                ]

                license_file = io.BytesIO(
                    json.dumps(license_dict, indent=4).encode("utf-8")
                )
                tarinfo = tarfile.TarInfo(name=f"licenses/{license.spdx_id}.json")
                tarinfo.size = len(license_file.getvalue())
                tar.addfile(tarinfo, license_file)

            for generic in Generic.objects.all():
                generic_json = serialize(
                    "json",
                    [generic],
                    use_natural_foreign_keys=True,
                    use_natural_primary_keys=True,
                )
                # Filter shared fields
                generic_dict = json.loads(generic_json)[0]
                generic_dict = {
                    k: v
                    for k, v in generic_dict["fields"].items()
                    if k in GENERIC_SHARED_FIELDS
                }
                generic_file = io.BytesIO(
                    json.dumps(generic_dict, indent=4).encode("utf-8")
                )
                filename = unicodedata.normalize("NFKD", generic.name)
                filename = re.sub(r"[^\w\s-]", "", filename).strip().lower()
                filename = re.sub(r"[-\s]+", "-", filename)
                tarinfo = tarfile.TarInfo(name=f"generics/{filename}.json")
                tarinfo.size = len(generic_file.getvalue())
                tar.addfile(tarinfo, generic_file)

        return tar_buffer.getvalue()


@transaction.atomic()
def handle_licenses_json_or_shared_json(data):
    """
    Support direct importing of licenses from a shared.json file
    from hermine-data repository as well as importing
    licenses from licenses.json files exported from Hermine UI.
    """
    dict = json.loads(data)
    if "objects" in dict:
        for obj in deserialize(
            "python",
            dict["objects"],
        ):
            obj.save()
        logger.info("Import a shared.json file directly into database.")
        return

    for obj in deserialize("json", data, handle_forward_references=True):
        from cube.models import Generic

        # Legacy, allow import of license without generics
        if "generic" in [f.cache_name for f in obj.deferred_fields.keys()]:
            name = obj.deferred_fields[
                next(f for f in obj.deferred_fields.keys() if f.cache_name == "generic")
            ][0]
            Generic.objects.get_or_create(name=name)

        # Create missing teams on the fly
        if "team" in [f.cache_name for f in obj.deferred_fields.keys()]:
            team = obj.deferred_fields[
                next(f for f in obj.deferred_fields.keys() if f.cache_name == "team")
            ][0]
            from cube.models import Team

            Team.objects.get_or_create(name=team)

        create_or_replace_by_natural_key(obj)
