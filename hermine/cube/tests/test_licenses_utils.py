#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
import unittest

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
from cube.utils.licenses import get_usages_obligations, is_ambiguous


class ObligationsTestCase(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create()
        self.release1 = Release.objects.create(product=self.product1)
        self.component1 = Component.objects.create()
        self.version1 = Version.objects.create(component=self.component1)

        self.license1 = License.objects.create()
        self.generic1 = Generic.objects.create()
        self.obligation1 = Obligation.objects.create(
            name="obligation1", license=self.license1, generic=self.generic1
        )
        self.obligation2 = Obligation.objects.create(
            name="obligation2", license=self.license1
        )
        self.usage1 = Usage.objects.create(release=self.release1, version=self.version1)
        self.usage1.licenses_chosen.set([self.license1])

    def test_simple_usage_obligation(self):
        generics, licenses = get_usages_obligations([self.usage1])

        self.assertIn(self.generic1, generics)
        self.assertIn(self.license1, licenses)

    def test_non_triggering_modification_obligation(self):
        self.obligation1.trigger_mdf = Usage.MODIFICATION_ALTERED
        self.obligation1.save()

        generics, licenses = get_usages_obligations([self.usage1])
        self.assertNotIn(self.generic1, generics)

    def test_triggering_modification_obligation(self):
        self.obligation1.trigger_mdf = Usage.MODIFICATION_ALTERED
        self.obligation1.save()
        self.usage1.component_modified = Usage.MODIFICATION_ALTERED
        self.usage1.save()

        generics, licenses = get_usages_obligations([self.usage1])
        self.assertIn(self.generic1, generics)

    def test_only_non_source_trigger(self):
        self.obligation1.trigger_expl = Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE
        self.obligation1.save()

        generics, licenses = get_usages_obligations([self.usage1])
        self.assertIn(self.generic1, generics)

    def test_triggering_explotation_source_only(self):
        self.usage1.exploitation = Usage.EXPLOITATION_DISTRIBUTION_SOURCE
        self.usage1.save()

        generics, licenses = get_usages_obligations([self.usage1])
        self.assertIn(self.generic1, generics)

    def test_non_triggering_explotation(self):
        self.obligation1.trigger_expl = Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE
        self.obligation1.save()
        self.usage1.exploitation = Usage.EXPLOITATION_DISTRIBUTION_SOURCE
        self.usage1.save()

        generics, licenses = get_usages_obligations([self.usage1])
        self.assertNotIn(self.generic1, generics)


class SPDXToolsTestCase(unittest.TestCase):
    def test_is_ambiguous(self):
        self.assertFalse(is_ambiguous("MIT"))
        self.assertFalse(is_ambiguous("MIT OR BSD"))
        self.assertTrue(is_ambiguous("MIT AND BSD"))
        self.assertFalse(is_ambiguous("MIT OR (BSD AND GPL-3.0-or-later)"))
        self.assertFalse(is_ambiguous("MIT OR(BSD AND GPL-3.0-or-later)"))
