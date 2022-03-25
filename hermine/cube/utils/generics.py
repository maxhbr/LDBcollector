#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import json

from django.core.serializers import serialize

from cube.models import Generic
from cube.serializers import GenericSerializer


def export_generics(indent=False):
    return serialize("json", Generic.objects.all(), indent=4 if indent else None)


def handle_generics_json(data):
    genericsArray = json.load(data)
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
    print(f"Generics : {created} created / {updated} updated")
