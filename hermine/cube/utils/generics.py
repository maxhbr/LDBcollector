#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import json
import logging

from django.core.serializers import serialize, deserialize
from django.db import transaction, IntegrityError

from cube.models import Generic, Team
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
    for generic in deserialize("json", data, handle_forward_references=True):
        try:
            generic.object.id = Generic.objects.get(name=generic.object.name).id
            updated += 1
        except Generic.DoesNotExist:
            created += 1

        if len(generic.deferred_fields) > 0:
            name = generic.deferred_fields[list(generic.deferred_fields.keys())[0]][0]
            Team.objects.create(name=name)

        generic.save()
        generic.save_deferred_fields()

    logger.info(f"Generics : {created} created / {updated} updated")

    return
