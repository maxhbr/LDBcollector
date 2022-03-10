#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.test import TestCase

from cube.models import (
    Usage,
    Obligation,
    License,
    Product,
    Release,
    Component,
    Version,
    Generic,
)
from cube.utils.licenses import get_usages_obligations


class ObligationsTestCase(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create()
        self.release1 = Release.objects.create(product=self.product1)
        self.component1 = Component.objects.create()
        self.version1 = Version.objects.create(component=self.component1)

        self.license1 = License.objects.create()
        self.generic1 = Generic.objects.create()
        self.obligation1 = Obligation.objects.create(
            license=self.license1, generic=self.generic1
        )
        self.obligation2 = Obligation.objects.create(license=self.license1)
        self.usage1 = Usage.objects.create(release=self.release1, version=self.version1)
        self.usage1.licenses_chosen.set([self.license1])

    def test_simple_usage_obligation(self):
        generics, licenses = get_usages_obligations([self.usage1])

        self.assertIn(self.generic1, generics)
        self.assertIn(self.license1, licenses)

    def test_not_triggered_obligation(self):
        self.obligation1.trigger_mdf = Usage.MODIFICATION_ALTERED
        self.obligation1.save()

        generics, licenses = get_usages_obligations([self.usage1])
        self.assertNotIn(self.generic1, generics)

    def test_triggered_modified_obligation(self):
        self.obligation1.trigger_mdf = Usage.MODIFICATION_ALTERED
        self.obligation1.save()
        self.usage1.component_modified = Usage.MODIFICATION_ALTERED
        self.usage1.save()

        generics, licenses = get_usages_obligations([self.usage1])
        self.assertIn(self.generic1, generics)
