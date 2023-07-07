# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.contrib.auth.models import Group
from django.test import TestCase

from cube.models import (
    Product,
    Component,
    Version,
)


# Models TestCases
class ProductTest(TestCase):
    fixtures = ["test_data.json"]

    def create_product(
        self, name="product creation test", description="yes, this is only a test"
    ):
        return Product.objects.create(name=name, description=description, owner=None)

    def test_product_creation(self):
        p = self.create_product()
        self.assertTrue(isinstance(p, Product))
        self.assertEqual(p.__str__(), p.name)


class ComponentTestCase(TestCase):
    def test_version_purl_updates_component_repo(self):
        component = Component.objects.create(name="component")
        Version.objects.create(
            component=component, version_number="1", purl="pkg:npm/namespace/package@1"
        )
        component.refresh_from_db()
        self.assertEqual(component.purl_type, "npm")


class DefaultPermissionTestCase(TestCase):
    def default_groups_have_permissions(self):
        pm = Group.objects.get(name="Project manager (install preset)")
        self.assertTrue(pm.permissions.filter(codename="view_product").exists())
