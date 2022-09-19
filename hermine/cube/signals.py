#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.db.models.signals import post_save
from django.dispatch import receiver
from packageurl import PackageURL

from cube.models import Version, Exploitation


@receiver(post_save, sender=Version, dispatch_uid="update_component_repository")
def update_component_repository(sender, instance: Version, created, **kwargs):
    if instance.purl and created:
        try:
            purl = PackageURL.from_string(instance.purl)
        except ValueError:
            pass
        else:
            instance.component.package_repo = purl.to_dict()["type"]
            instance.component.save()


@receiver(post_save, sender=Exploitation, dispatch_uid="update_usages_exploitations")
def update_usages_exploitations(sender, instance: Exploitation, created, **kwargs):
    instance.release.usage_set.filter(
        project=instance.project, scope=instance.scope
    ).update(exploitation=instance.exploitation)
