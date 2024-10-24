# Generated by Django 4.1 on 2022-08-10 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cube", "0014_alter_component_name_alter_component_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="obligation",
            name="trigger_expl",
            field=models.CharField(
                choices=[
                    (
                        "DistributionSourceDistributionNonSource",
                        "If the component is distributed as source code or as binary",
                    ),
                    (
                        "DistributionSource",
                        "If the component is distributed as source code",
                    ),
                    (
                        "DistributionNonSource",
                        "If the component is distributed as binary",
                    ),
                    ("NetworkAccess", "If component is accessible by network access"),
                    ("InternalUse", "If the component is used internally"),
                ],
                default="DistributionSourceDistributionNonSource",
                max_length=40,
            ),
        ),
        migrations.AlterField(
            model_name="obligation",
            name="trigger_mdf",
            field=models.CharField(
                choices=[
                    ("Altered", "Only if the component is modified"),
                    ("Unmodified", "Only if the component is not modified"),
                    ("AlteredUnmodified", "Whether the component is modified or not"),
                ],
                default="AlteredUnmodified",
                max_length=40,
            ),
        ),
    ]
