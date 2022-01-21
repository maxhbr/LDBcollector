# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.test import TestCase, Client
from django.urls import reverse
from cube.models import *
from cube.forms import *
from cube.views import ReleaseView
from cube.f_views import explode_SPDX_to_units


class ExplodeSPDXReleaseViewTests(TestCase):
    def test_complicated_SPDX_expr(self):
        """
        An SPDX expression that comes with all the difficulties one may face.
        """
        SPDX_complex = "(MIT AND (BSD-3-Clause-No-Nuclear-License-2014 OR GPL-3.0-or-later WITH GPL-3.0-linking-source-exception OR GPL-2.0-only WITH Classpath-exception-2.0)) OR (AGPL-3.0-or-later WITH PS-or-PDF-font-exception-20170817 AND  Condor-1.1 AND (TORQUE-1.1 OR Artistic-1.0-cl8 OR MIT))"
        SPDX_exploded = [
            "MIT",
            "BSD-3-Clause-No-Nuclear-License-2014",
            "GPL-3.0-or-later WITH GPL-3.0-linking-source-exception",
            "GPL-2.0-only WITH Classpath-exception-2.0",
            "AGPL-3.0-or-later WITH PS-or-PDF-font-exception-20170817",
            "Condor-1.1",
            "TORQUE-1.1",
            "Artistic-1.0-cl8",
        ]
        explosion = explode_SPDX_to_units(SPDX_complex)
        self.assertEqual(explosion, SPDX_exploded)
