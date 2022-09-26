#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from itertools import groupby

from django.core.management import BaseCommand
from packageurl import PackageURL

from cube.models import Component


def _details_from_version(v):
    if not v.purl:
        return "", ""
    purl = PackageURL.from_string(v.purl)
    return purl.type, (f"{purl.namespace}/{purl.name}" if purl.namespace else purl.name)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for c in Component.objects.all():
            components_versions = []
            versions = sorted(list(c.versions.all()), key=lambda v: v.purl)

            for unique_component, versions in groupby(versions, _details_from_version):
                components_versions.append((unique_component, list(versions)))
                if len(list(versions)) > 0 and (
                    c.package_repo != unique_component[0]
                    or c.name != unique_component[1]
                ):
                    print(
                        "\nComponent name or repository is inconsistent with versions Package URL : "
                    )
                    print(f"Component {c.id} {c.name}")
                    for v in versions:
                        print(f"Version {v.id} {v.purl}")
