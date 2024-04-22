#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from itertools import groupby

from django.core.management import BaseCommand
from django.db import transaction, IntegrityError
from packageurl import PackageURL
from tqdm import tqdm

from cube.models import Component, Version


def _details_from_version(v):
    if not v.purl:
        return "", ""
    purl = PackageURL.from_string(v.purl)
    return purl.type, (f"{purl.namespace}/{purl.name}" if purl.namespace else purl.name)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--fix", action="store_true")

    @transaction.atomic()
    def handle(self, fix=False, *args, **kwargs):
        self.stdout.write(
            "Checking components names consistency with versions Package URLs"
        )
        report = ""
        changes = 0
        creations = 0

        for c in tqdm(Component.objects.all(), total=Component.objects.all().count()):
            unique_components_count = 0
            versions = sorted(list(c.versions.all()), key=lambda v: v.purl)

            for component_details, versions in groupby(versions, _details_from_version):
                unique_components_count += 1
                component_versions = list(versions)

                if (
                    # skip if no data in versions attached
                    not (len(component_versions) > 0 and component_versions[0].purl)
                ) or (
                    # skip if component matches versions
                    unique_components_count == 1
                    and (
                        c.name == component_details[1]
                        or c.purl_type == component_details[0]
                    )
                ):
                    continue

                # if first component only need to update
                if unique_components_count == 1:
                    report += f"\nid: {c.id} \n"
                    if c.name != component_details[1]:
                        report += f"name: {c.name} -> " + self.style.NOTICE(
                            f"{component_details[1]}\n"
                        )
                        if fix:
                            c.name = component_details[1]
                        changes += 1
                    if c.purl_type != component_details[0]:
                        report += f"purl_type: {c.purl_type} -> " + self.style.NOTICE(
                            f"{component_details[0]}\n"
                        )
                        if fix:
                            c.purl_type = component_details[0]
                        changes += 1
                    if fix:
                        try:
                            with transaction.atomic():
                                c.save()
                        except IntegrityError:
                            c = Component.objects.get(
                                name=component_details[1],
                                purl_type=component_details[0],
                            )
                            Version.objects.filter(
                                pk__in=[v.id for v in component_versions]
                            ).update(component=c)
                # if several unique components detected in version purls, we need to create new objects
                else:
                    report += self.style.ERROR("\nnew component\n")
                    report += "name: " + self.style.ERROR(component_details[1] + "\n")
                    report += "type: " + self.style.ERROR(component_details[0] + "\n")
                    if fix:
                        c = Component.objects.create(
                            name=component_details[1], purl_type=component_details[0]
                        )
                        Version.objects.filter(
                            pk__in=[v.id for v in component_versions]
                        ).update(component=c)
                    creations += 1

                report += "versions:\n"
                for v in component_versions:
                    report += f" * {v.id} ({v.purl})\n"

        self.stdout.write(report + "\n")
        if fix:
            self.stdout.write(
                self.style.NOTICE(f"{changes} fields changed\n")
                + self.style.ERROR(f"{creations} objects created\n")
            )
        else:
            self.stdout.write(
                self.style.NOTICE(f"{changes} fields need changes\n")
                + self.style.ERROR(f"{creations} objects needs to be created")
                + (
                    "\nRun with --fix option to apply changes"
                    if changes or creations
                    else ""
                )
            )
