# Generated by Django 4.0.6 on 2022-07-21 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cube", "0010_remove_category_products_product_categories"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="categories",
            field=models.ManyToManyField(
                blank=True, db_table="cube_category_products", to="cube.category"
            ),
        ),
    ]
