#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List

import yaml
from semantic_version.base import BaseSpec, SimpleSpec, AllOf, Range

from cube.models import LicenseCuration


# See https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-curations-yml.md
# and https://github.com/oss-review-toolkit/ort/blob/main/examples/curations.yml for export format


@dataclass
class ArtifactHash:
    value: str
    algorith: str


@dataclass
class RemoteArtifact:
    url: str
    hash: ArtifactHash


@dataclass
class VCS:
    type: str
    url: str
    revision: str
    path: str


@dataclass
class Curation:
    comment: str | None = None
    purl: str | None = None
    cpe: str | None = None
    authors: List[str] = None
    concluded_license: str | None = None
    description: str | None = None
    homepage_url: str | None = None
    binary_artifact: RemoteArtifact | None = None
    source_artifact: RemoteArtifact | None = None
    vcs: VCS | None = None


@dataclass
class CurationEntry:
    id: str
    curations: Curation

    def __init__(
        self,
        curations: Curation,
        type: str,
        name: str,
        namespace: str = "",
        version: str | BaseSpec | None = None,
    ):
        type = fix_type_case(type)
        self.id = f"{type}:{namespace}:{name}"
        if isinstance(version, str) and version != "":
            self.id += f":{version}"

        if isinstance(version, SimpleSpec):
            self.id += f":{simple_spec_to_ivy_string(version)}"

        self.curations = curations


def fix_type_case(type: str):
    """
    ORT type list from https://github.com/oss-review-toolkit/ort/blob/4fd94d67ed456a47981dca89315d74f2161eccd4/model/src/main/kotlin/utils/Extensions.kt
    """
    try:
        return {
            "bower": "Bower",
            "cocoapods": "CocoaPods",
            "composer": "Composer",
            "crate": "Crate",
            "dotnet": "DotNet",
            "nuget": "NuGet",
            "gem": "Gem",
            "godep": "GoDep",
            "gomod": "GoMod",
            "maven": "Maven",
            "npm": "NPM",
            "pypi": "PyPI",
            "pub": "Pub",
        }[type]
    except KeyError:
        return type


def simple_spec_to_ivy_string(spec: SimpleSpec):
    clause = spec.clause.simplify()
    if isinstance(clause, AllOf):
        clauses = clause.clauses
    else:
        clauses = [clause]

    if not all(isinstance(clause, Range) for clause in clauses):
        raise ValueError("This version constraint is not supported by ORT")

    if len(clauses) > 2:
        raise ValueError("This version constraint is not supported by ORT")

    min = [
        clause
        for clause in clauses
        if isinstance(clause, Range) and clause.operator in [Range.OP_GTE, Range.OP_GT]
    ]
    max = [
        clause
        for clause in clauses
        if isinstance(clause, Range) and clause.operator in [Range.OP_LTE, Range.OP_LT]
    ]

    if len(min) == 0 and len(max) == 0:
        raise ValueError("This version constraint is not supported by ORT")

    if len(min) == 0:
        left = "("
    elif min[0].operator == Range.OP_GTE:
        left = f"[{min[0].target}"
    else:
        left = f"]{min[0].target}"

    if len(max) == 0:
        right = ")"
    elif max[0].operator == Range.OP_LTE:
        right = f"{max[0].target}]"
    else:
        right = f"{max[0].target}["

    return f"{left},{right}"


def version_constraint_is_ort_compatible(version_constraint: SimpleSpec):
    try:
        simple_spec_to_ivy_string(version_constraint)
        return True
    except ValueError:
        return False


def hermine_to_ort(curation: LicenseCuration):
    if curation.version is not None:
        component = curation.version.component

    elif curation.component is not None:
        component = curation.component
    else:
        raise ValueError("Component unspecified")

    if component.namespace and component.name.startswith(component.namespace):
        name = component.name.replace(f"{component.namespace}/", "", 1)
    else:
        name = component.name

    return CurationEntry(
        curations=Curation(
            comment=curation.explanation,
            concluded_license=curation.expression_out,
        ),
        type=fix_type_case(component.purl_type),
        namespace=component.namespace or "",
        name=name,
        version=curation.version.version_number
        if curation.version is not None
        else curation.version_constraint,
    )


def export_curations(queryset):
    return yaml.dump(
        list(
            asdict(
                hermine_to_ort(curation),
                dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
            )
            for curation in queryset.exclude(version=None, component=None)
            if curation.is_ort_compatible
        ),
        sort_keys=False,
    )
