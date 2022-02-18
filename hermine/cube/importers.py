# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

import json
import yaml
import re
import spdx_license_list
from datetime import datetime
from cube.models import Component, Version, Usage
from rest_framework.parsers import JSONParser
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
                try:
                    vers_lic_proc = package["package"]["declared_licenses_processed"][
                        "spdx_expression"
                    ]
                except:
                    vers_lic_proc = ""
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


def import_ort_evaluated_model_json_file(json_file, release_id):
    data = json.load(json_file)

    for package in data["packages"]:
        if package["is_project"]:
            continue
        component, component_created = Component.objects.get_or_create(
            name=package["purl"].split("@")[0].split(":")[1],
            defaults={
                "description": package["description"],
                "homepage_url": package["homepage_url"],
            },
        )
        if component_created:
            print("Component " + component.name + " created")

        version, version_created = Version.objects.get_or_create(
            component=component,
            version_number=package["purl"].split("@")[1],
            defaults={
                "declared_license_expr": [
                    data["licenses"][license_index]
                    for license_index in package["declared_licenses"]
                ],
                "spdx_valid_license_expr": package["declared_licenses_processed"][
                    "spdx_expression"
                ],
                # TODO : support ORT scanner function
                # "scanned_licenses":
                "purl": package["purl"],
            },
        )
        if version_created:
            print(
                "Version "
                + version.version_number
                + " created for component "
                + component.name
            )

        # Project_id is the name of the project of the package
        project_id = [
            data["packages"][path["project"]]
            for path in data["paths"]
            if path["pkg"] == package["_id"]
        ][0]["id"]

        for scope_index in package["scopes"]:
            scope = data["scopes"][scope_index]["name"]  # or "Blank Scope"
            usage, usage_created = Usage.objects.get_or_create(
                version_id=version.id,
                release_id=release_id,
                scope=scope,
                description=project_id,
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


def import_spdx_file(yaml_file, release_id):
    # Importing SPDX BOM yaml
    print("YAML import started", datetime.now())
    data = yaml.safe_load(yaml_file)
    for package in data["packages"]:
        current_scope = "Global"
        comp_name = package["name"].rsplit("@")[0]
        comp_url = package["downloadLocation"]
        comp, created = Component.objects.get_or_create(
            name=comp_name, defaults={"homepage_url": comp_url}
        )
        # If necessary create version
        if "versionInfo" not in package:
            vers_number = "Current"
        else:
            vers_number = package["versionInfo"]
        # SPDX output sometimes return "NOASSERTION" instead of an empty value. Handling that.
        if package["licenseDeclared"] != "NOASSERTION":
            vers_lic_decl = package["licenseDeclared"]
        else:
            vers_lic_decl = ""
        vers_lic_concl = package["licenseConcluded"]
        vers, vcreated = Version.objects.get_or_create(
            component=comp,
            version_number=vers_number,
            defaults={
                "declared_license_expr": vers_lic_decl,
                "spdx_valid_license_expr": vers_lic_concl,
            },
        )
        version_id = vers.id
        u, ucreated = Usage.objects.get_or_create(
            version_id=version_id,
            release_id=release_id,
            scope=current_scope,
            defaults={"addition_method": "Scan"},
        )
    print("YAML import done", datetime.now())
