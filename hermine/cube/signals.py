#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from packageurl import PackageURL

from cube.models import Version, Exploitation, License
from cube.utils.spdx import explode_spdx_to_units

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Version, dispatch_uid="update_component_repository")
def update_component_repository(sender, instance: Version, created, **kwargs):
    if instance.purl and created:
        try:
            purl = PackageURL.from_string(instance.purl)
        except ValueError:
            pass
        else:
            instance.component.purl_type = purl.to_dict()["type"]
            instance.component.save()


@receiver(post_save, sender=Exploitation, dispatch_uid="update_usages_exploitations")
def update_usages_exploitations(sender, instance: Exploitation, created, **kwargs):
    instance.release.usage_set.filter(
        project=instance.project, scope=instance.scope
    ).update(exploitation=instance.exploitation)


@receiver(post_save, sender=Version, dispatch_uid="create_missing_licenses")
def create_missing_licenses(sender, instance: Version, created, **kwargs):
    if not instance.effective_license:
        return

    spdx_licenses = explode_spdx_to_units(instance.effective_license)

    for spdx_license in spdx_licenses:
        logger.info("unknown license", spdx_license)
        License.objects.get_or_create(spdx_id=spdx_license)
