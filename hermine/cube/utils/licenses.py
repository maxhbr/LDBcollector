# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from cube.models import License
from cube.serializers import LicenseSerializer


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
    try:
        license_instance = License.objects.get(spdx_id=license_dict["spdx_id"])
    except License.DoesNotExist:
        print("Instantiation of a new License: ", license_dict["spdx_id"])
        license_instance = License(spdx_id=license_dict["spdx_id"])
        license_instance.save()
    s = LicenseSerializer(license_instance, data=license_dict)
    s.is_valid(raise_exception=True)
    print(s.errors)
    s.save()


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
            # Those two lines allow filtering obligations depending on the Usage
            # context (if the component has been modified and how it's being
            # distributed)
            obligations_filtered = license.obligation_set.filter(
                trigger_mdf__contains=usage.component_modified
            )
            obligations_filtered = [
                o
                for o in obligations_filtered
                if match_obligation_exploitation(usage.exploitation, o.trigger_expl)
            ]
            for obligation in obligations_filtered:
                if obligation.generic:
                    generics_involved.add(obligation.generic)
                else:
                    orphaned_licenses.add(license)
    return generics_involved, orphaned_licenses


def match_obligation_exploitation(expl, explTrigger):
    """
    A small utility to check the pertinence of an Obligation in the exploitation
    context of a usage.

    :param expl: The type of exploitation of the component
    :type expl: A string in ["Distribution", "DistributionSource",
        "DistributionNonSource", "NetworkA "Network access"),ccess", "InternalUse"
    :param explTrigger: The type of exploitation that triggers the obligation
    :type explTrigger: A string in ["Distribution", "DistributionSource",
        "DistributionNonSource", "NetworkA "Network access"),ccess", "InternalUse"
    :return: True if the exploitation meets the exploitation trigger
    :rtype: Boolean
    """
    if explTrigger in expl:
        return True
    elif (
        explTrigger == "DistributionSource" or explTrigger == "DistributionNonSource"
    ) and expl == "Distribution":
        return True
    else:
        return False
