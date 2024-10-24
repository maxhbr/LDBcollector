# Generated by Django 4.0.6 on 2022-07-07 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cube", "0009_alter_license_options"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name="category",
                    name="products",
                ),
                migrations.AddField(
                    model_name="product",
                    name="categories",
                    field=models.ManyToManyField(
                        db_table="cube_category_products", to="cube.category"
                    ),
                ),
            ],
        )
    ]
