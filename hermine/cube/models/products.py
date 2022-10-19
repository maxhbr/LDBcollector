#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse_lazy


class Product(models.Model):
    """
    A product which dependencies are to be audited.
    """

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(
        "Category", db_table="cube_category_products", blank=True
    )

    def get_absolute_url(self):
        return reverse_lazy("cube:product_detail", args=[self.id])

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    A category of product
    """

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product category"
        verbose_name_plural = "Product categories"


class Release(models.Model):
    """
    A specific release of a product
    """

    SHIPPING_CHOICES = [
        ("Archived", "Archived"),
        ("Active", "In developpement"),
        ("Published", "Published"),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="releases"
    )
    release_number = models.CharField(max_length=200)
    ship_status = models.CharField(max_length=20, choices=SHIPPING_CHOICES, blank=True)
    pub_date = models.DateTimeField("date published", blank=True, null=True)
    # First unvalidated step : 6 = all are validated
    valid_step = models.IntegerField("Validation Step", blank=True, null=True)
    commit = models.CharField("Commit hash or ref", max_length=255, blank=True)

    def __str__(self):
        return self.product.__str__() + " " + self.release_number

    class Meta:
        unique_together = ["product", "release_number"]
        verbose_name = "Product release"
        verbose_name_plural = "Product releases"


class Exploitation(models.Model):
    """
    Stores how a release is exploited (so all its Usage can be updated accordingly)
    """

    from cube.models.components import Usage

    release = models.ForeignKey(
        Release, on_delete=models.CASCADE, related_name="exploitations"
    )
    scope = models.CharField(max_length=50)
    project = models.CharField(max_length=750, blank=True)
    exploitation = models.CharField(
        max_length=50,
        choices=Usage.EXPLOITATION_CHOICES,
        default=Usage.EXPLOITATION_CHOICES[0][0],
    )

    def __str__(self):
        return self.release.__str__() + " : " + str(self.scope)

    class Meta:
        unique_together = ["release", "scope", "project"]
