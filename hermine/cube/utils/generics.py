#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import logging

from django.core.serializers import serialize, deserialize
from django.db import transaction

from cube.models import Generic, Team
from cube.utils.importers import create_or_replace_by_natural_key

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
        if len(generic.deferred_fields) > 0:
            name = generic.deferred_fields[list(generic.deferred_fields.keys())[0]][0]
            Team.objects.get_or_create(name=name)

        if create_or_replace_by_natural_key(generic):
            created += 1
        else:
            updated += 1

    logger.info(f"Generics : {created} created / {updated} updated")
