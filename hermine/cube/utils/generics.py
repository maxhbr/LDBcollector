#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import json
import logging

from django.core.serializers import serialize
from django.db import transaction

from cube.models import Generic
from cube.serializers import GenericSerializer

logger = logging.getLogger(__name__)


def export_generics(indent=False):
    serializer = GenericSerializer(Generic.objects.all(), many=True)
    data = json.dumps(serializer.data, indent=4 if indent else None)
    return serialize("json", Generic.objects.all(), indent=4 if indent else None)


@transaction.atomic()
def handle_generics_json(data):
    genericsArray = json.loads(data)
    created, updated = 0, 0
    for generic in genericsArray:
        try:
            g = Generic.objects.get(pk=generic["pk"])
            updated += 1
        except Generic.DoesNotExist:
            g = Generic(generic["pk"])
            created += 1
        s = GenericSerializer(g, data=generic["fields"], partial=True)
        s.is_valid(raise_exception=True)
        s.save()
    logger.info(f"Generics : {created} created / {updated} updated")
