# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from datetime import datetime
import json

from django.db import transaction
from rest_framework.parsers import JSONParser
from spdx.parsers import (
    jsonparser,
    jsonyamlxmlbuilders,
    tagvaluebuilders,
    rdf,
    rdfbuilders,
    tagvalue,
    xmlparser,
    yamlparser,
)
from spdx.parsers.loggers import StandardLogger
import spdx_license_list

from cube.models import Component, Version, Usage
from cube.serializers import LicenseSerializer


def import_licenses_file(licenses):
    licenses_data = JSONParser().parse(licenses)
    for license_data in licenses_data:
        serializer = LicenseSerializer(data=license_data)
        if serializer.is_valid():
            serializer.save()
        else:
            print("could not import license data, serializer invalid")


def is_spdx(expression):
    # Checks if elements of an expression are spdx compliant
    # But doesn't check if the expression itself is.
    # Like "AND OR MIT BSD-3-Clause" would pass
    operators = ["AND", "OR", "WITH", "(", ")"]
    chunks = expression.split()
    valid = True
    for chunk in chunks:
        if (chunk not in operators) and (chunk not in spdx_license_list.LICENSES):
            valid = False
            print(chunk, "not spdx")
    return valid


def import_ort_file(json_file, release_id):
    # Importing data from ORT's analyzer
    def add_package(package_id, current_scope, current_project):
        if package_id in ref_packages:
            package = ref_packages[package_id]["package"]
            if "version_id" not in ref_packages[package_id]:
                # If necessary create component
                comp_name = package["package"]["purl"].split("@")[0].split(":")[1]
                comp_description = package["package"]["description"]
                comp_url = package["package"]["homepage_url"]
                comp, created = Component.objects.get_or_create(
                    name=comp_name,
                    defaults={
                        "description": comp_description,
                        "homepage_url": comp_url,
                    },
                )
                if created:
                    print("Component " + comp_name + " created")
                # If necessary create version
                vers_number = package["package"]["purl"].split("@")[1]
                vers_lic_decl = package["package"]["declared_licenses"]
                vers_lic_proc = package["package"]["declared_licenses_processed"].get(
                    "spdx_expression", ""
                )
                if package_id in scan_packages:
                    vers_scan_lic = ",".join(scan_packages[package_id])
                    print(vers_scan_lic)
                else:
                    vers_scan_lic = ""
                vers, vcreated = Version.objects.get_or_create(
                    component=comp,
                    version_number=vers_number,
                    defaults={
                        "declared_license_expr": vers_lic_decl,
                        "spdx_valid_license_expr": vers_lic_proc,
                        "scanned_licenses": vers_scan_lic,
                        "purl": package["package"]["purl"],
                    },
                )
                version_id = vers.id
                ref_packages[package_id]["version_id"] = version_id

            else:
                version_id = ref_packages[package_id]["version_id"]
            u, ucreated = Usage.objects.get_or_create(
                version_id=version_id,
                release_id=release_id,
                scope=current_scope,
                description=current_project,
                defaults={"addition_method": "Scan"},
            )
        else:
            print(package_id, " not found or already treated")

    def parse_deps(dep, current_scope, current_project):
        # used to parse recursively the dep tree
        add_package(dep["id"], current_scope, current_project)
        if "dependencies" in dep:
            for dependency in dep["dependencies"]:
                parse_deps(dependency, current_scope, current_project)

    def parse_root(dep_root, current_scope, current_project):
        # used to parse the new dep tree
        pkg_index = dep_root["pkg"]
        full_name = data["analyzer"]["result"]["dependency_graphs"][prefix]["packages"][
            pkg_index
        ]
        print("dependency:", full_name, "for", current_scope, current_project)
        add_package(full_name, current_scope, current_project)
        if "dependencies" in dep_root:
            for dep in dep_root["dependencies"]:
                parse_root(dep, current_scope, current_project)

    data = json.load(json_file)
    print("file loaded ", datetime.now())
    # Create a dict with packages'ORTid and (later) hermine version id
    ref_packages = dict()
    for package in data["analyzer"]["result"]["packages"]:
        ref_packages[package["package"]["id"]] = dict()
        ref_packages[package["package"]["id"]]["package"] = package
    print("packages parsed ", datetime.now())
    # Create a dict with pkg ids and corresponding scope_root id
    # ref_scop_root["NPM"][id of the package]= id of the scope_root
    if "dependency_graphs" in data["analyzer"]["result"]:
        ref_scop_root = dict()
        for prefix in list(data["analyzer"]["result"]["dependency_graphs"].keys()):
            ref_scop_root[prefix] = dict()
            for index, scop_root in enumerate(
                data["analyzer"]["result"]["dependency_graphs"][prefix]["scopes"]
            ):
                if "pkg" in scop_root:
                    ref_scop_root[prefix][str(scop_root["pkg"])] = index
    # Parse scanned packages
    scan_packages = dict()
    if data["scanner"]:
        for scan_pack in data["scanner"]["results"]["scan_results"]:
            scan_licenses = set()
            for scan_license in scan_pack["results"][0]["summary"]["licenses"]:
                scan_licenses.add(scan_license["license"])
            scan_packages[scan_pack["id"]] = scan_licenses
    # Parse the tree of projects/Scopes of the analyzer
    for project in data["analyzer"]["result"]["projects"]:
        project_name = project["id"]
        if "scopes" in project:
            for scope in project["scopes"]:
                scope_name = scope["name"]
                if scope["name"] is None:
                    scope_name = "Blank Scope"
                for root_dependency in scope["dependencies"]:
                    parse_deps(root_dependency, scope_name, project_name)
        # If "scope_names" in project, it means the projects use the new dep tree

        elif "scope_names" in project:
            prefix = project_name.split(":")[0]
            radical = ":".join([project_name.split(":")[2], project_name.split(":")[3]])
            for scope_name in project["scope_names"]:
                full_scope = ":" + radical + ":" + scope_name
                # We get the root *packages* of the scope
                roots = data["analyzer"]["result"]["dependency_graphs"][prefix][
                    "scopes"
                ][full_scope]
                for root in roots:
                    root_pkg_index = root["root"]
                    print("Root :", root_pkg_index)
                    root_pkg_ORT_id = data["analyzer"]["result"]["dependency_graphs"][
                        prefix
                    ]["packages"][root_pkg_index]
                    print("Root_pkg_ort :", root_pkg_ORT_id)
                    # If this root packages has dependencies it should be in the dict
                    if str(root_pkg_index) in ref_scop_root[prefix]:
                        scope_root_idx = ref_scop_root[prefix][str(root_pkg_index)]
                        scope_root = data["analyzer"]["result"]["dependency_graphs"][
                            prefix
                        ]["scopes"][scope_root_idx]
                        parse_root(scope_root, scope_name, project_name)

                    else:
                        # Todo we should add the package itself
                        # That's one more reason to refactor the code
                        # introducing a "add_package() function
                        add_package(root_pkg_ORT_id, scope_name, project_name)
        else:
            print("NO SCOPES FOR Project Id", project["id"])


@transaction.atomic()
def import_ort_evaluated_model_json_file(json_file, release_idk, replace=False):
    data = json.load(json_file)

    if replace:
        Usage.objects.filter(release=release_idk).delete()

    for package in data["packages"]:
        if package["is_project"]:
            continue
        component, component_created = Component.objects.get_or_create(
            name=package["purl"].split("@")[0].split(":")[1],
            defaults={
                "description": package.get("description", ""),
                "homepage_url": package.get("homepage_url", ""),
            },
        )
        if component_created:
            print(f"Component {component.name} created")
        else:
            print(f"Component {component.name} already there")

        declared_licenses_indices = package.get("declared_licenses", "")
        declared_licenses = ""
        if declared_licenses_indices:
            declared_licenses = " ; ".join(
                [
                    data["licenses"][license_index]["id"]
                    for license_index in declared_licenses_indices
                ]
            )
        else:
            declared_licenses = ""
        print(f"declared_licenses {declared_licenses}")
        version, version_created = Version.objects.get_or_create(
            component=component,
            version_number=package["purl"].split("@")[1],
            defaults={
                "declared_license_expr": declared_licenses,
                "spdx_valid_license_expr": package["declared_licenses_processed"].get(
                    "spdx_expression", ""
                ),
                # TODO : support ORT scanner function
                # "scanned_licenses":
                "purl": package["purl"],
            },
        )
        if version_created:
            print(
                f"Version {version.version_number} created for component {component.name}"
            )

        # As we don't yet take into account the concept of subprojects
        # we store them in the description
        related_projects = []
        for path in package["paths"]:
            related_projects.append(
                data["packages"][data["paths"][path]["project"]]["id"]
            )
        description = "\n".join(related_projects)
        scope_indices = package.get("scopes")
        if scope_indices is None or len(scope_indices) == 0:
            scopes = {"Blank Scope"}
        else:
            scopes = set()
            for scope_index in scope_indices:
                scopes.add(data["scopes"][scope_index]["name"])
        for scope in scopes:
            usage, usage_created = Usage.objects.get_or_create(
                version_id=version.id,
                release_id=release_id,
                scope=scope,
                description=description,
                # defaults={"addition_method": "Scan"},
            )


def import_yocto_file(manifest_file, release_id):
    # Importing data from Yocto's license.manifest

    def spdxify(ylicense):
        equivalents = {
            "|": "OR",
            "&": "AND",
            "LGPLv2.1": "LGPL-2.1",
            "GPLv2": "GPL-2.0",
            "+": "-or-later",
            "-with-": " WITH ",
        }
        substitutes = {
            "GPL-2.0": "GPL-2.0-only",
            "LGPL-2.0": "LGPL-2.0-only",
            "LGPL-2.1": "LGPL-2.1-only",
            "AFL-2": "AFL-2.0",
        }
        chunks = ylicense.split()
        for i in range(0, len(chunks)):
            for kw in equivalents:
                chunks[i] = chunks[i].replace(kw, equivalents[kw])
            if chunks[i] in substitutes:
                chunks[i] = substitutes[chunks[i]]
        spdxlicense = " ".join(chunks)
        return spdxlicense

    def insert_package(package):
        # If necessary create component
        comp_name = "/".join(["yocto", package["recipe"], package["name"]])
        comp, created = Component.objects.get_or_create(name=comp_name)
        vers_number = package["version"]
        vers_lic_decl = package["corrected_license"]
        vers_lic_proc = package["spdx_license"]
        vers, vcreated = Version.objects.get_or_create(
            component=comp,
            version_number=vers_number,
            defaults={
                "declared_license": vers_lic_decl,
                "spdx_valid_license_expr": vers_lic_proc,
                "purl": package["purl"],
            },
        )
        version_id = vers.id
        u, ucreated = Usage.objects.get_or_create(
            version_id=version_id,
            release_id=release_id,
            scope="rootfs",
            defaults={"addition_method": "Scan"},
        )

    print("Importing yocto data, starting :", datetime.now())
    read_data = manifest_file.read().decode()
    lines = read_data.split("\n")
    package = dict()
    list_pack = list()

    for line in lines:
        radical = line.split(":")[0].strip()
        if len(line.split(":")) > 1:
            value = line.split(":")[1].strip()
        if radical == "PACKAGE NAME":
            package["name"] = value
        elif radical == "PACKAGE VERSION":
            package["version"] = value
        elif radical == "RECIPE NAME":
            package["recipe"] = value
        elif radical == "LICENSE":
            yoctolic = value
            package["license"] = yoctolic
            package["corrected_license"] = spdxify(yoctolic)
            if is_spdx(package["corrected_license"]):
                package["spdx_license"] = package["corrected_license"]
            else:
                package["spdx_license"] = ""
            package["purl"] = "@".join(
                [
                    "/".join(["pkg:yocto", package["recipe"], package["name"]]),
                    package["version"],
                ]
            )
            list_pack.append(package)
            package = dict()
    for pack in list_pack:
        insert_package(pack)
    print("Importing yocto data, ending :", datetime.now())


@transaction.atomic()
def import_spdx_file(spdx_file, release_id, replace=False):
    # Importing SPDX BOM yaml
    print("SPDX import started", datetime.now())
    document, error = parse_spdx_file(spdx_file)
    if error:
        print("SPDX file contains errors (printed above), but import continues…")

    if replace:
        Usage.objects.filter(release=release_id).delete()

    for package in document.packages:
        current_scope = "Global"
        comp_name = package.name.rsplit("@")[0]
        comp_url = package.download_location
        comp, created = Component.objects.get_or_create(
            name=comp_name, defaults={"homepage_url": comp_url}
        )
        # If necessary create version
        vers_number = package.version or "Current"
        vers_lic_decl = package.license_declared.identifier
        # SPDX output sometimes return "NOASSERTION" instead of an empty value.
        if vers_lic_decl == "NOASSERTION":
            vers_lic_decl = ""
        vers_lic_concl = package.conc_lics.identifier
        vers, vcreated = Version.objects.get_or_create(
            component=comp,
            version_number=vers_number,
            defaults={
                "declared_license_expr": vers_lic_decl,
                "spdx_valid_license_expr": vers_lic_concl,
            },
        )
        version_id = vers.id
        usage, usage_created = Usage.objects.get_or_create(
            version_id=version_id,
            release_id=release_id,
            scope=current_scope,
            defaults={"addition_method": "Scan"},
        )
    print("SPDX import done", datetime.now())


# Function derivated from
# https://github.com/spdx/tools-python/blob/21ea183f72a1179c62ec146a992ec5642cc5f002/spdx/parsers/parse_anything.py
# SPDX-FileCopyrightText: spdx contributors
# SPDX-License-Identifier: Apache-2.0
def parse_spdx_file(spdx_file):
    builder_module = jsonyamlxmlbuilders
    filename = spdx_file.name
    read_data = False
    if filename.endswith(".rdf") or filename.endswith(".rdf.xml"):
        parsing_module = rdf
        builder_module = rdfbuilders
    elif filename.endswith(".spdx"):
        parsing_module = rdf
        builder_module = rdfbuilders
    elif filename.endswith(".tag"):
        parsing_module = tagvalue
        builder_module = tagvaluebuilders
        read_data = True
    elif filename.endswith(".json"):
        parsing_module = jsonparser
    elif filename.endswith(".xml"):
        parsing_module = xmlparser
    elif filename.endswith(".yaml") or filename.endswith(".yml"):
        parsing_module = yamlparser
    else:
        return None, "FileType Not Supported" + filename

    parser = parsing_module.Parser(builder_module.Builder(), StandardLogger())
    if hasattr(parser, "build"):
        parser.build()
    if read_data:
        data = spdx_file.read()
        return parser.parse(data)
    else:
        return parser.parse(spdx_file)
