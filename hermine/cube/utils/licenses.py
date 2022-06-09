# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
import json
import re
from typing import Iterable

from cube.models import License, Obligation
from cube.serializers import LicenseSerializer


def is_ambiguous(spdx_expression: str):
    """
    Because of unreliable metadata, many "Licence1 AND Licence2" expressions
    actually meant to be "Licence1 OR Licence2". This function checks weither
    an expressions can be trusted or not.

    :param spdx_expression: an expression to test
    :type spdx_expression: str
    :return: whether expression needs to be confirmed
    :rtype: bool
    """
    return re.search(r"[)\s]AND[(\s]", spdx_expression) and not re.search(
        r"[)\s]OR[(\s]", spdx_expression
    )


def check_licenses_against_policy(release):
    response = {}
    usages_lic_red = set()
    usages_lic_orange = set()
    usages_lic_grey = set()
    involved_lic = set()

    derogations = release.derogation_set.all()
    usages = release.usage_set.all()

    release_derogs = dict()
    for derog in derogations:
        if derog.license.id not in release_derogs:
            release_derogs[derog.license.id] = dict()
            release_derogs[derog.license.id]["usages"] = set()
            release_derogs[derog.license.id]["scopes"] = set()
        if derog.usage:
            release_derogs[derog.license.id]["usages"].add(derog.usage)
        if derog.scope:
            release_derogs[derog.license.id]["scopes"].add(derog.scope)

    for usage in usages:
        for license in usage.licenses_chosen.all():
            involved_lic.add(license)
            derogate = (license.id in release_derogs) and (
                (
                    not (release_derogs[license.id]["usages"])
                    and not (release_derogs[license.id]["scopes"])
                )
                or usage in release_derogs[license.id]["usages"]
                or usage.scope in release_derogs[license.id]["scopes"]
            )
            if license.color == "Red" and not derogate:
                usages_lic_red.add(usage)
            elif license.color == "Orange" and not derogate:
                usages_lic_orange.add(usage)
            elif license.color == "Grey" and not derogate:
                usages_lic_grey.add(usage)

    response["usages_lic_red"] = usages_lic_red
    response["usages_lic_orange"] = usages_lic_orange
    response["usages_lic_grey"] = usages_lic_grey
    response["involved_lic"] = involved_lic
    response["derogations"] = derogations

    return response


def get_licenses_to_check_or_create(release):
    response = {}
    validated_usages = release.usage_set.all().filter(
        version__spdx_valid_license_expr__isnull=False
    )
    corrected_usages = release.usage_set.all().filter(
        version__corrected_license__isnull=False
    )
    validated_usages |= corrected_usages
    licenses_to_check = set()
    licenses_to_create = set()
    for usage in validated_usages:
        if usage.version.corrected_license:
            raw_expression = usage.version.corrected_license
        else:
            raw_expression = usage.version.spdx_valid_license_expr
        SPDX_Licenses = explode_SPDX_to_units(raw_expression)

        for license in SPDX_Licenses:
            try:
                license_instance = License.objects.get(spdx_id=license)
                if license_instance.color == "Grey":
                    licenses_to_check.add(license_instance)
            except License.DoesNotExist:
                # It might happen that SPDX throws 'NOASSERTION' instead of an empty
                # string. Handling that.
                if license != "NOASSERTION":
                    licenses_to_create.add(license)
                    print("unknown license", license)

    response["licenses_to_check"] = licenses_to_check
    response["licenses_to_create"] = licenses_to_create
    return response


def explode_SPDX_to_units(SPDX_expr):
    """Extract a list of every license from a SPDX valid expression.

    :param SPDX_expr: A string that represents a valid SPDX expression. (Like ")
    :type SPDX_expr: string
    :return: A list of valid SPDX licenses contained in the expression.
    :rtype: list
    """
    licenses = []
    raw_expression = SPDX_expr.replace("(", "").replace(")", "")
    # Next line allows us to consider an SPDX expression that has a 'WITH' clause as a
    # full SPDX expression
    raw_expression = raw_expression.replace(" WITH ", "_WITH_")
    chunks = raw_expression.split()
    while "AND" in chunks:
        chunks.remove("AND")
    while "OR" in chunks:
        chunks.remove("OR")
    i = 0
    while i < len(chunks):
        if chunks[i] not in licenses:
            chunks[i] = chunks[i].replace("_WITH_", " WITH ")
            licenses.append(chunks[i])
        i += 1
    return licenses


def create_or_update_license(license_dict):
    create = False
    try:
        license_instance = License.objects.get(spdx_id=license_dict["spdx_id"])
    except License.DoesNotExist:
        license_instance = License(spdx_id=license_dict["spdx_id"])
        license_instance.save()
        create = True
    s = LicenseSerializer(license_instance, data=license_dict)
    s.is_valid(raise_exception=True)
    s.save()
    return create


def get_license_triggered_obligations(
    license: License, exploitation: str = None, modification: str = None
):
    """
    Get triggered obligations for a licence and a usage context
    (if the component has been modified and how it's being distributed)

    :param license: A License instance
    :param exploitation: A value from Usage.EXPLOITATION_CHOICES
    :param modification: A value from Usage.MODIFICATION_CHOICES
    :return: A queryset or list of Obligation instances
    """
    obligations = license.obligation_set.all()

    if exploitation is not None:
        obligations = obligations.filter(trigger_mdf__contains=modification)

    if modification is not None:
        obligations = [
            o
            for o in obligations
            if (
                o.trigger_expl in exploitation or exploitation in o.trigger_expl
            )  # Poor man bitwise OR
        ]

    return obligations


def get_licenses_triggered_obligations(
    licenses: Iterable[License], exploitation: str = None, modification: str = None
):
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

    :param usages: A iterable of Usage objects
    :return: A tuple with a list of generic and a list of licenses which obligations have no generics
    """
    generics_involved = set()
    orphaned_licenses = set()

    for usage in usages:
        for license in usage.licenses_chosen.all():
            for obligation in get_license_triggered_obligations(
                license, usage.exploitation, usage.component_modified
            ):
                if obligation.generic:
                    generics_involved.add(obligation.generic)
                else:
                    orphaned_licenses.add(license)
    return generics_involved, orphaned_licenses


def export_licenses(indent=False):
    serializer = LicenseSerializer(License.objects.all(), many=True)
    data = json.dumps(serializer.data, indent=4 if indent else None)
    return data


def handle_licenses_json(data):
    licenseArray = json.load(data)
    # Handling case of a JSON that only contains one license and is not a list
    # (single license purpose)
    if type(licenseArray) is dict:
        create_or_update_license(licenseArray)
    # Handling case of a JSON that contains multiple licenses and is a list
    # (multiple licenses purpose)
    elif type(licenseArray) is list:
        created, updated = 0, 0
        for license in licenseArray:
            if create_or_update_license(license):
                created += 1
            else:
                updated += 1

        print(f"Licenses : {created} created / {updated} updated")
    else:
        print("Type of JSON neither is a list nor a dict")
