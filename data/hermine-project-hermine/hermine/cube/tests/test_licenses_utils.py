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
from cube.utils.licenses import (
    get_usages_obligations,
)


class ObligationsTestCase(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create()
        self.release1 = Release.objects.create(product=self.product1)
        self.component1 = Component.objects.create()
        self.version1 = Version.objects.create(component=self.component1)

        self.license1 = License.objects.create(spdx_id="LicenseRef-FakeLicense-1.0")
        self.generic1 = Generic.objects.create()
        self.obligation_with_generic = Obligation.objects.create(
            name="obligation1", license=self.license1, generic=self.generic1
        )
        self.obligation_specific = Obligation.objects.create(
            name="obligation2", license=self.license1
        )
        self.usage1 = Usage.objects.create(
            release=self.release1,
            version=self.version1,
            license_expression=self.license1.spdx_id,
        )

    def test_simple_usage_obligation(self):
        generics, specifics, licenses_involved = get_usages_obligations([self.usage1])

        self.assertIn(self.generic1, generics)
        self.assertIn(self.license1, licenses_involved)

    def test_non_triggering_modification_obligation(self):
        self.obligation_with_generic.trigger_mdf = Usage.MODIFICATION_ALTERED
        self.obligation_with_generic.save()

        generics, specifics, licenses_involved = get_usages_obligations([self.usage1])
        self.assertNotIn(self.generic1, generics)

    def test_triggering_modification_obligation(self):
        self.obligation_with_generic.trigger_mdf = Usage.MODIFICATION_ALTERED
        self.obligation_with_generic.save()
        self.usage1.component_modified = Usage.MODIFICATION_ALTERED
        self.usage1.save()

        generics, specifics, licenses_involved = get_usages_obligations([self.usage1])
        self.assertIn(self.generic1, generics)

    def test_only_non_source_trigger(self):
        self.obligation_with_generic.trigger_expl = (
            Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE
        )
        self.obligation_with_generic.save()

        generics, specifics, licenses_involved = get_usages_obligations([self.usage1])
        self.assertIn(self.generic1, generics)

    def test_triggering_exploitation_source_only(self):
        self.usage1.exploitation = Usage.EXPLOITATION_DISTRIBUTION_SOURCE
        self.usage1.save()

        generics, specifics, licenses_involved = get_usages_obligations([self.usage1])
        self.assertIn(self.generic1, generics)

    def test_non_triggering_exploitation(self):
        self.obligation_with_generic.trigger_expl = (
            Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE
        )
        self.obligation_with_generic.save()
        self.usage1.exploitation = Usage.EXPLOITATION_DISTRIBUTION_SOURCE
        self.usage1.save()

        generics, specifics, licenses_involved = get_usages_obligations([self.usage1])
        self.assertNotIn(self.generic1, generics)

    def test_non_triggering_modification_and_exploitation(self):
        self.obligation_with_generic.trigger_mdf = Usage.MODIFICATION_ALTERED
        self.obligation_with_generic.trigger_expl = (
            Usage.EXPLOITATION_DISTRIBUTION_SOURCE
        )
        self.obligation_with_generic.save()

        self.usage1.component_modified = Usage.MODIFICATION_UNMODIFIED
        self.usage1.exploitation = Usage.EXPLOITATION_NETWORK
        self.usage1.save()

        generics, specifics, licenses_involved = get_usages_obligations([self.usage1])
        self.assertNotIn(self.generic1, generics)
        self.assertNotIn(self.obligation_specific, specifics)
