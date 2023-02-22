#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.core.exceptions import ValidationError
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
    is_ambiguous,
    explode_spdx_to_units,
    get_ands_corrections,
)
from cube.utils.validators import validate_spdx_expression


class ObligationsTestCase(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create()
        self.release1 = Release.objects.create(product=self.product1)
        self.component1 = Component.objects.create()
        self.version1 = Version.objects.create(component=self.component1)

        self.license1 = License.objects.create()
        self.generic1 = Generic.objects.create()
        self.obligation_with_generic = Obligation.objects.create(
            name="obligation1", license=self.license1, generic=self.generic1
        )
        self.obligation_specific = Obligation.objects.create(
            name="obligation2", license=self.license1
        )
        self.usage1 = Usage.objects.create(release=self.release1, version=self.version1)
        self.usage1.licenses_chosen.set([self.license1])

    def test_simple_usage_obligation(self):
        generics, specifics, licenses_involved = get_usages_obligations([self.usage1])

        self.assertIn(self.generic1, generics)
        self.assertIn(self.license1, licenses)

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


class SPDXToolsTestCase(TestCase):
    def test_is_ambiguous(self):
        self.assertFalse(is_ambiguous("MIT"))
        self.assertFalse(is_ambiguous("MIT OR BSD"))
        self.assertTrue(is_ambiguous("MIT AND BSD"))
        self.assertFalse(is_ambiguous("MIT OR (BSD AND GPL-3.0-or-later)"))
        self.assertFalse(is_ambiguous("MIT OR(BSD AND GPL-3.0-or-later)"))

    def test_validate_spdx_license(self):
        with self.assertRaises(ValidationError):
            validate_spdx_expression("foo")
        validate_spdx_expression("LicenseRef-FakeLicense-1.0")
        validate_spdx_expression("GPL-3.0-or-later")

        with self.assertRaises(ValidationError):
            validate_spdx_expression("LicenseRef-FakeLicense-1.0 OR Foo")


class ExplodeSPDXTestCase(TestCase):
    def test_complicated_SPDX_expr(self):
        """
        An SPDX expression that comes with all the difficulties one may face.
        """
        SPDX_complex = (
            "(MIT AND (BSD-3-Clause-No-Nuclear-License-2014 OR"
            + " GPL-3.0-or-later WITH GPL-3.0-linking-source-exception OR GPL-2.0-only"
            + " WITH Classpath-exception-2.0)) OR (AGPL-3.0-or-later WITH"
            + " PS-or-PDF-font-exception-20170817 AND  Condor-1.1 AND"
            + " (TORQUE-1.1 OR Artistic-1.0-cl8 OR MIT))"
        )
        SPDX_exploded = [
            "AGPL-3.0-or-later WITH PS-or-PDF-font-exception-20170817",
            "Artistic-1.0-cl8",
            "BSD-3-Clause-No-Nuclear-License-2014",
            "Condor-1.1",
            "GPL-2.0-only WITH Classpath-exception-2.0",
            "GPL-3.0-or-later WITH GPL-3.0-linking-source-exception",
            "MIT",
            "TORQUE-1.1",
        ]
        explosion = explode_spdx_to_units(SPDX_complex)
        self.assertEqual(explosion, SPDX_exploded)


class GetAndsCorrectionsTestCase(TestCase):
    def test_basic_get_ands_corrections(self):
        # basic
        self.assertEqual(
            get_ands_corrections("MIT AND X11"),
            {"MIT AND X11", "MIT OR X11"},
        )

    def test_not_ambiguous_expression(self):
        self.assertEqual(get_ands_corrections("MIT OR X11"), {"MIT OR X11"})

    def test_three_members_expression(self):
        self.assertEqual(
            get_ands_corrections("MIT AND X11 AND WTFPL"),
            {"MIT AND WTFPL AND X11", "MIT OR WTFPL OR X11"},
        )

    def test_subexpressions(self):
        self.assertEqual(
            get_ands_corrections("MIT AND (X11 AND WTFPL)"),
            {
                "MIT AND WTFPL AND X11",
                "MIT OR WTFPL OR X11",
                "MIT OR (WTFPL AND X11)",
                "MIT AND (WTFPL OR X11)",
            },
        )
        self.assertEqual(
            get_ands_corrections("(MIT AND X11) AND WTFPL"),
            {
                "MIT AND WTFPL AND X11",
                "MIT OR WTFPL OR X11",
                "WTFPL AND (MIT OR X11)",
                "WTFPL OR (MIT AND X11)",
            },
        )
