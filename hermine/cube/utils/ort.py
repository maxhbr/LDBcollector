#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Mapping, List

import yaml

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
    declared_license_mapping: Mapping[str, str] = None
    description: str | None = None
    homepage_url: str | None = None
    binary_artifact: RemoteArtifact | None = None
    source_artifact: RemoteArtifact | None = None
    vcs: VCS | None = None
    is_meta_data_only: bool | None = None
    is_modified: bool | None = None


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
        version=None,
    ):
        type = fix_type_case(type)
        self.id = f"{type}:{namespace}:{name}"
        if version is not None:
            self.id += f":{version}"
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
            declared_license_mapping={curation.expression_in: curation.expression_out},
            is_meta_data_only=False,
            is_modified=False,
        ),
        type=fix_type_case(component.package_repo),
        namespace=component.namespace or "",
        name=name,
        version=curation.version.version_number
        if curation.version is not None
        else None,
    )


def export_curations(queryset):
    return yaml.dump(
        list(
            asdict(
                hermine_to_ort(curation),
                dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
            )
            for curation in queryset.exclude(version=None, component=None)
        ),
        sort_keys=False,
    )
