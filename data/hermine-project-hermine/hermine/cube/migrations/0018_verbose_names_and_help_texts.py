# Generated by Django 4.1.1 on 2022-09-26 12:37

from django.db import migrations, models
import django.db.models.deletion

import cube.utils.validators


class Migration(migrations.Migration):
    dependencies = [
        ("cube", "0017_rename_color_explanation_license_allowed_explanation"),
    ]

    operations = [
        migrations.RenameField(
            model_name="license",
            old_name="non_commmercial",
            new_name="non_commercial",
        ),
        migrations.AlterField(
            model_name="component",
            name="name",
            field=models.CharField(
                help_text="Unique name of the FOSS component.", max_length=200
            ),
        ),
        migrations.AlterField(
            model_name="component",
            name="package_repo",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="Package repository"
            ),
        ),
        migrations.AlterField(
            model_name="exploitation",
            name="release",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exploitations",
                to="cube.release",
            ),
        ),
        migrations.AlterField(
            model_name="generic",
            name="description",
            field=models.TextField(
                blank=True, help_text="Longer description, optional.", max_length=500
            ),
        ),
        migrations.AlterField(
            model_name="generic",
            name="in_core",
            field=models.BooleanField(
                default=False,
                help_text="If True, means this Generic obligation is assumed to systematically fit to the enterprise policy. Otherwise, means it has to be manually checked.",
            ),
        ),
        migrations.AlterField(
            model_name="generic",
            name="metacategory",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Communication", "Communication constraints"),
                    ("IPManagement", "IP management"),
                    ("LicenseAgreement", "License agreement"),
                    ("Mentions", "Mentions"),
                    ("ProvidingSourceCode", "Providing source code"),
                    ("TechnicalConstraints", "Technical constraints"),
                ],
                help_text="A category of Generic obligation.",
                max_length=40,
            ),
        ),
        migrations.AlterField(
            model_name="generic",
            name="name",
            field=models.CharField(
                help_text="Short description of the Generic obligation. Unique.",
                max_length=200,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="generic",
            name="passivity",
            field=models.CharField(
                blank=True,
                choices=[("Active", "Active"), ("Passive", "Passive")],
                help_text="A Generic obligation needs to conduct some kind of action(Active) or NOT to do specific things (Passive)",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="license",
            name="allowed",
            field=models.CharField(
                blank=True,
                choices=[
                    ("always", "Always allowed"),
                    ("never", "Never allowed"),
                    ("context", "Allowed depending on context"),
                    ("", "Not reviewed yet"),
                ],
                max_length=20,
                verbose_name="OSS Policy",
            ),
        ),
        migrations.AlterField(
            model_name="license",
            name="allowed_explanation",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="OSS Policy explanation"
            ),
        ),
        migrations.AlterField(
            model_name="license",
            name="copyleft",
            field=models.CharField(
                blank=True,
                choices=[
                    ("None", "Permissive"),
                    ("Strong", "Strong copyleft"),
                    ("Weak", "Weak copyleft"),
                    ("Network", "Strong network copyleft"),
                    ("NetworkWeak", "Weak network copyleft"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="license",
            name="fsf_approved",
            field=models.BooleanField(null=True, verbose_name="FSF Approved"),
        ),
        migrations.AlterField(
            model_name="license",
            name="inspiration",
            field=models.ForeignKey(
                blank=True,
                help_text="A Licence which inspired this one",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="cube.license",
            ),
        ),
        migrations.AlterField(
            model_name="license",
            name="inspiration_spdx",
            field=models.CharField(
                blank=True,
                default="",
                help_text="SPDX Identifier of another license which inspired this one",
                max_length=200,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="license",
            name="long_name",
            field=models.CharField(blank=True, max_length=200, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="license",
            name="osi_approved",
            field=models.BooleanField(null=True, verbose_name="OSI Approved"),
        ),
        migrations.AlterField(
            model_name="license",
            name="spdx_id",
            field=models.CharField(
                max_length=200, unique=True, verbose_name="SPDX Identifier"
            ),
        ),
        migrations.AlterField(
            model_name="license",
            name="status",
            field=models.CharField(
                choices=[
                    ("Checked", "Checked"),
                    ("Pending", "Pending"),
                    ("To_Discuss", "To discuss"),
                    ("To_Check", "To check"),
                ],
                default="To check",
                max_length=20,
                verbose_name="Review status",
            ),
        ),
        migrations.AlterField(
            model_name="obligation",
            name="license",
            field=models.ForeignKey(
                help_text="The License instance that implies the current obligation.",
                on_delete=django.db.models.deletion.CASCADE,
                to="cube.license",
            ),
        ),
        migrations.AlterField(
            model_name="obligation",
            name="passivity",
            field=models.CharField(
                blank=True,
                choices=[("Active", "Active"), ("Passive", "Passive")],
                help_text='If the obligation is "Active" (under certain condition you SHOULD perform some action) or"Passive" (under certain condition you SHOULD NOT do something)',
                max_length=20,
            ),
        ),
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
                help_text="The context necessary to trigger this obligation",
                max_length=40,
                verbose_name="Triggering exploitation context",
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
                help_text="Status of modication necessary to trigger this obligation",
                max_length=40,
                verbose_name="Triggering modifications",
            ),
        ),
        migrations.AlterField(
            model_name="obligation",
            name="verbatim",
            field=models.TextField(
                help_text="Full text of the obligation, out of the license itself",
                max_length=4000,
            ),
        ),
        migrations.AlterField(
            model_name="usagedecision",
            name="expression_in",
            field=models.CharField(
                help_text="The exact expression which must be changed", max_length=500
            ),
        ),
        migrations.AlterField(
            model_name="usagedecision",
            name="expression_out",
            field=models.CharField(
                help_text="The expression which will replace `expression_in`",
                max_length=500,
                validators=[cube.utils.validators.validate_spdx_expression],
            ),
        ),
        migrations.AlterField(
            model_name="version",
            name="corrected_license",
            field=models.CharField(
                blank=True,
                help_text="Final license expression used in legal evaluation",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="version",
            name="declared_license_expr",
            field=models.CharField(
                blank=True,
                help_text="Declared license expression (may not be SPDX valid)",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="version",
            name="purl",
            field=models.CharField(
                blank=True,
                help_text="Package URL (https://github.com/package-url/purl-spec)",
                max_length=250,
            ),
        ),
        migrations.AlterField(
            model_name="version",
            name="spdx_valid_license_expr",
            field=models.CharField(
                blank=True,
                help_text="License expression validated by user",
                max_length=200,
            ),
        ),
    ]
