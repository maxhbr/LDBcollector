#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.db.models.signals import post_save
from django.dispatch import receiver
from packageurl import PackageURL

from cube.models import Version


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
