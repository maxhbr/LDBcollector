#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.test import TestCase

from cube.utils.spdx import (
    is_ambiguous,
    has_ors,
    is_valid,
    explode_spdx_to_units,
    get_ands_corrections,
)


class SPDXToolsTestCase(TestCase):
    def test_is_ambiguous(self):
        self.assertFalse(is_ambiguous("MIT"))
        self.assertFalse(is_ambiguous("MIT OR BSD"))
        self.assertTrue(is_ambiguous("MIT AND BSD"))
        self.assertFalse(is_ambiguous("MIT OR (BSD AND GPL-3.0-or-later)"))
        self.assertFalse(is_ambiguous("MIT OR(BSD AND GPL-3.0-or-later)"))

    def test_has_ors(self):
        self.assertFalse(has_ors("MIT"))
        self.assertTrue(has_ors("MIT OR BSD"))

    def test_or_later_has_ors(self):
        self.assertFalse(has_ors("GPL-3.0-only"))
        self.assertFalse(has_ors("GPL-3.0"))

        self.assertTrue(has_ors("GPL-3.0-or-later"))
        self.assertTrue(has_ors("GPL-2.0-or-later WITH Classpath-exception-2.0"))
        self.assertTrue(has_ors("GPL-3.0-or-later AND BSD"))

        self.assertTrue(has_ors("GPL-3.0+"))
        self.assertTrue(has_ors("GPL-2.0+ WITH Classpath-exception-2.0"))

    def test_is_valid_spdx_license(self):
        self.assertFalse(is_valid("foo"))
        self.assertTrue(is_valid("LicenseRef-FakeLicense-1.0"))
        self.assertTrue(is_valid("GPL-3.0-or-later"))
        self.assertFalse(is_valid("LicenseRef-FakeLicense-1.0 OR Foo"))


class ExplodeSPDXTestCase(TestCase):
    def test_explode_SPDX_expr(self):
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
