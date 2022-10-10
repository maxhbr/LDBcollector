#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import json
import logging

from django.core.serializers import serialize, deserialize
from django.db import transaction, IntegrityError

from cube.models import Generic
from cube.serializers import GenericSerializer

logger = logging.getLogger(__name__)


def export_generics(indent=False):
    return serialize(
        "json",
        Generic.objects.all(),
        indent=4 if indent else None,
        use_natural_foreign_keys=True,
        use_natural_primary_keys=True,
    )


@transaction.atomic()
def handle_generics_json(data):
    created, updated = 0, 0
    for generic in deserialize("json", data):
        try:
            generic.object.id = Generic.objects.get(name=generic.object.name).id
            generic.save()
            updated += 1
        except Generic.DoesNotExist:
            generic.save()
            created += 1

    logger.info(f"Generics : {created} created / {updated} updated")

    return
