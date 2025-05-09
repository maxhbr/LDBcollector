# Generated by Django 4.0.6 on 2022-07-29 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cube", "0011_alter_product_categories"),
    ]

    operations = [
        migrations.RenameModel("LicenseChoice", "UsageDecision"),
        migrations.CreateModel(
            name="ExpressionValidation",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cube.usagedecision",),
        ),
        migrations.CreateModel(
            name="LicenseChoice",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
                "verbose_name": "License choice rule",
                "verbose_name_plural": "License choice rules",
            },
            bases=("cube.usagedecision",),
        ),
        migrations.AddField(
            model_name="usagedecision",
            name="decision_type",
            field=models.CharField(
                choices=[
                    ("choice", "License choice"),
                    ("validation", "Expression validation"),
                ],
                default="choice",
                max_length=500,
            ),
            preserve_default=False,
        ),
    ]
