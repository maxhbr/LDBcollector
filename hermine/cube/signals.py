#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from packageurl import PackageURL

from cube.models import Version, Exploitation, License, LicensePolicy, Usage
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
    usages = instance.release.usage_set.all()
    if instance.project:
        usages = usages.filter(project=instance.project)
    if instance.scope:
        usages = usages.filter(scope=instance.scope)

    usages.update(exploitation=instance.exploitation)


@receiver(post_save, sender=Version, dispatch_uid="create_missing_licenses")
def create_missing_licenses(sender, instance: Version, created, **kwargs):
    if not instance.effective_license:
        return

    spdx_licenses = explode_spdx_to_units(instance.effective_license)

    for spdx_license in spdx_licenses:
        logger.info("unknown license", spdx_license)
        License.objects.get_or_create(spdx_id=spdx_license)


@receiver(post_save, sender=License, dispatch_uid="create_missing_policies")
def create_missing_policies(sender, instance: License, created, **kwargs):
    LicensePolicy.objects.get_or_create(license=instance)


@receiver(post_save, sender=Usage, dispatch_uid="update_usage_licenses")
def update_licenses_chosen(sender, instance: Usage, **kwargs):
    licenses_spdx_ids = explode_spdx_to_units(instance.license_expression)
    usage_licenses = []
    try:
        for spdx_id in licenses_spdx_ids:
            licence_to_add = License.objects.get(spdx_id=spdx_id)
            usage_licenses.append(licence_to_add)
    except License.DoesNotExist:
        logger.warning(
            "%s : can not choose unknown license",
            instance.version,
        )
    instance.licenses_chosen.set(usage_licenses)
