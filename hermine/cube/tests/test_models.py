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
