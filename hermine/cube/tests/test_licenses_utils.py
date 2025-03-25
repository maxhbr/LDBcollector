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
    Compatibility,
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


class CompatibilityTestCase(TestCase):
    def test_empty_licenses_compatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_STRONG
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_NONE
        )
        self.assertFalse(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )
        self.assertTrue(
            license2.is_compatible_with(
                license1,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_outbound_permissive_license_compatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_NONE
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_NONE
        )
        Generic.objects.create()
        Obligation.objects.create(license=license1, generic=Generic.objects.first())
        self.assertTrue(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_outbound_permissive_license_copyleft_incompatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_STRONG
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_NONE
        )
        self.assertFalse(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_license_both_strong_copyleft_incompatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_STRONG
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_STRONG
        )
        self.assertFalse(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )
        self.assertFalse(
            license2.is_compatible_with(
                license1,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_outbound_copyleft_license_incompatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_NONE
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_STRONG
        )
        Obligation.objects.create(license=license1)
        self.assertFalse(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_outbound_copyleft_license_subset_compatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_NONE
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_STRONG
        )
        Generic.objects.create()
        Obligation.objects.create(license=license2, generic=Generic.objects.first())
        Obligation.objects.create(license=license1, generic=Generic.objects.first())
        self.assertTrue(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_aggregation_compatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_STRONG
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_NONE
        )
        Obligation.objects.create(license=license2)
        self.assertTrue(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_AGGREGATION,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )
        # If copyleft is outbound side, linking or exploitation does not matter
        self.assertFalse(
            license2.is_compatible_with(
                license1,
                Usage.LINKING_AGGREGATION,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_weak_copyleft_linking_compatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_WEAK
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_NONE
        )
        Obligation.objects.create(license=license2)
        self.assertTrue(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_DYNAMIC,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )
        # If copyleft is outbound side, linking or exploitation does not matter
        self.assertFalse(
            license2.is_compatible_with(
                license1,
                Usage.LINKING_DYNAMIC,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_explicit_compatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_STRONG
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_STRONG
        )
        compatibility = Compatibility.objects.create(
            from_license=license1,
            to_license=license2,
            direction=Compatibility.DIRECTION_ASCENDING,
        )
        self.assertTrue(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )
        self.assertFalse(
            license2.is_compatible_with(
                license1,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

        compatibility.direction = Compatibility.DIRECTION_DESCENDING
        compatibility.save()
        self.assertFalse(
            license1.is_compatible_with(
                license2,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )
        self.assertTrue(
            license2.is_compatible_with(
                license1,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_no_outbound_license_incompatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_STRONG
        )
        Generic.objects.create(name="generic1")
        Obligation.objects.create(
            license=license1, generic=Generic.objects.get(name="generic1")
        )
        self.assertFalse(
            license1.is_compatible_with(
                None,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )

    def test_no_outbound_license_internal_compatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_STRONG
        )
        Generic.objects.create(name="generic1")
        Obligation.objects.create(
            license=license1, generic=Generic.objects.get(name="generic1")
        )
        self.assertTrue(
            license1.is_compatible_with(
                None, Usage.LINKING_MINGLED, Usage.EXPLOITATION_INTERNAL
            )
        )

    def test_no_outbound_network_compatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_STRONG
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=License.COPYLEFT_NETWORK
        )
        self.assertTrue(
            license1.is_compatible_with(
                None, Usage.LINKING_MINGLED, Usage.EXPLOITATION_NETWORK
            )
        )
        self.assertFalse(
            license2.is_compatible_with(
                None, Usage.LINKING_MINGLED, Usage.EXPLOITATION_NETWORK
            )
        )

    def test_license_without_copyleft_raises(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=""
        )
        license2 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-2.0", copyleft=""
        )
        with self.assertRaises(ValueError):
            license1.is_compatible_with(
                license2,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        with self.assertRaises(ValueError):
            license2.is_compatible_with(
                license1,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )

    def test_self_compatibility(self):
        license1 = License.objects.create(
            spdx_id="LicenseRef-FakeLicense-1.0", copyleft=License.COPYLEFT_STRONG
        )
        Obligation.objects.create(license=license1)
        self.assertTrue(
            license1.is_compatible_with(
                license1,
                Usage.LINKING_MINGLED,
                Usage.EXPLOITATION_DISTRIBUTION_NONSOURCE,
            )
        )
