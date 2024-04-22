#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.core.serializers.base import DeserializedObject


def create_or_replace_by_natural_key(proxy_object: DeserializedObject):
    object_class = proxy_object.object.__class__
    try:
        key = list(proxy_object.object.natural_key())
        proxy_object.object.id = object_class.objects.get_by_natural_key(*key).id
        created = False
    except object_class.DoesNotExist:
        created = True

    proxy_object.save()
    proxy_object.save_deferred_fields()
    return created
