# Generated by Django 3.2.11 on 2022-01-21 14:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

from cube.utils.validators import validate_spdx_expression


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Component",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, unique=True)),
                ("package_repo", models.CharField(blank=True, max_length=200)),
                ("description", models.TextField(blank=True, max_length=500)),
                ("programming_language", models.CharField(blank=True, max_length=200)),
                ("spdx_expression", models.CharField(blank=True, max_length=200)),
                ("homepage_url", models.URLField(blank=True)),
                (
                    "export_control_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("CL", "Cleared"),
                            ("TBC", "To check"),
                            ("CONF", "Confirmed"),
                        ],
                        max_length=20,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Generic",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, unique=True)),
                ("description", models.TextField(blank=True, max_length=500)),
                ("in_core", models.BooleanField(default=False)),
                (
                    "metacategory",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Communication", "Communication constraints"),
                            ("IPManagement", "IP management"),
                            ("LicenseAgreement", "License agreement"),
                            ("Mentions", "Mentions"),
                            ("ProvidingSourceCode", "Providing source code"),
                            ("TechnicalConstraints", "Technical constraints"),
                        ],
                        max_length=40,
                    ),
                ),
                (
                    "passivity",
                    models.CharField(
                        blank=True,
                        choices=[("Active", "Active"), ("Passive", "Passive")],
                        max_length=20,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="License",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("spdx_id", models.CharField(max_length=200, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Checked", "Checked"),
                            ("Pending", "Pending"),
                            ("To_Discuss", "To discuss"),
                            ("To_Check", "To check"),
                        ],
                        default="To check",
                        max_length=20,
                    ),
                ),
                ("long_name", models.CharField(blank=True, max_length=200)),
                ("categories", models.CharField(blank=True, max_length=200)),
                ("license_version", models.CharField(blank=True, max_length=200)),
                ("radical", models.CharField(blank=True, max_length=200)),
                ("autoupgrade", models.BooleanField(null=True)),
                ("steward", models.CharField(blank=True, max_length=200)),
                (
                    "inspiration_spdx",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                (
                    "copyleft",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("None", "Persmissive"),
                            ("Strong", "Strong copyleft"),
                            ("Weak", "Weak copyleft"),
                            ("Network", "Strong network copyleft"),
                            ("NetworkWeak", "Weak network copyleft"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("Green", "Always allowed"),
                            ("Red", "Never allowed"),
                            ("Orange", "Allowed depending on context"),
                            ("Grey", "No reviewed yet"),
                        ],
                        default="Grey",
                        max_length=20,
                    ),
                ),
                ("color_explanation", models.CharField(blank=True, max_length=200)),
                ("url", models.URLField(blank=True)),
                ("osi_approved", models.BooleanField(null=True)),
                ("fsf_approved", models.BooleanField(null=True)),
                (
                    "foss",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Yes", "We consider it is FOSS"),
                            ("Yes-Auto", "FOSS - deduced"),
                            ("No", "We consider it is NOT FOSS"),
                            ("No-Auto", "NOT FOSS - deduced"),
                        ],
                        max_length=20,
                    ),
                ),
                ("patent_grant", models.BooleanField(null=True)),
                ("ethical_clause", models.BooleanField(null=True)),
                (
                    "non_commmercial",
                    models.BooleanField(
                        null=True, verbose_name="Only non-commercial use"
                    ),
                ),
                ("legal_uncertainty", models.BooleanField(null=True)),
                ("non_tivoisation", models.BooleanField(null=True)),
                ("technical_nature_constraint", models.BooleanField(null=True)),
                ("law_choice", models.CharField(blank=True, max_length=200)),
                ("venue_choice", models.CharField(blank=True, max_length=200)),
                ("comment", models.TextField(blank=True, max_length=1500)),
                (
                    "verbatim",
                    models.TextField(
                        blank=True,
                        help_text="Only necessary if the license has no official SPDX ID",
                    ),
                ),
                (
                    "inspiration",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="cube.license",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, unique=True)),
                ("description", models.TextField(blank=True, max_length=500)),
                (
                    "owner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Release",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("release_number", models.CharField(max_length=200)),
                (
                    "ship_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Archived", "Archived"),
                            ("Active", "In developpement"),
                            ("Published", "Published"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "pub_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="date published"
                    ),
                ),
                (
                    "valid_step",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Validation Step"
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cube.product"
                    ),
                ),
            ],
            options={
                "unique_together": {("product", "release_number")},
            },
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("icon", models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Version",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("version_number", models.CharField(max_length=200)),
                ("declared_license_expr", models.CharField(blank=True, max_length=200)),
                (
                    "spdx_valid_license_expr",
                    models.CharField(blank=True, max_length=200),
                ),
                ("corrected_license", models.CharField(blank=True, max_length=200)),
                ("purl", models.CharField(blank=True, max_length=250)),
                (
                    "component",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cube.component"
                    ),
                ),
            ],
            options={
                "unique_together": {("component", "version_number")},
            },
        ),
        migrations.CreateModel(
            name="Usage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Auto", "Auto validated"),
                            ("Unknown", "Unknown"),
                            ("Validated", "Validated"),
                            ("KO", "Problem"),
                            ("Fixed", "Problem solved"),
                        ],
                        default="Unknown",
                        max_length=20,
                    ),
                ),
                (
                    "addition_method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Scan", "Added by scan"),
                            ("Manual", "Added manually"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "addition_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="date added"
                    ),
                ),
                (
                    "linking",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Aggregation", "Mere aggregation"),
                            ("Dynamic", "Dynamic Linking"),
                            ("Static", "Static Linking"),
                            ("Package", "Package Manager"),
                            ("Mingled", "Source code directly derived"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "component_modified",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Altered", "Modified"),
                            ("Unmodified", "Not modified"),
                        ],
                        default="Unmodified",
                        max_length=20,
                    ),
                ),
                (
                    "exploitation",
                    models.CharField(
                        choices=[
                            ("Distribution", "Distribution source and object"),
                            ("DistributionSource", "Distribution - Source"),
                            ("DistributionNonSource", "Distribution Non source"),
                            ("NetworkAccess", "Network access"),
                            ("InternalUse", "Internal use"),
                        ],
                        default="Distribution",
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True, max_length=500)),
                ("scope", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "license_expression",
                    models.CharField(
                        blank=True,
                        max_length=500,
                        validators=[
                            validate_spdx_expression,
                        ],
                    ),
                ),
                (
                    "licenses_chosen",
                    models.ManyToManyField(blank=True, to="cube.License"),
                ),
                (
                    "release",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cube.release"
                    ),
                ),
                (
                    "version",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cube.version"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Obligation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("verbatim", models.TextField(max_length=4000)),
                (
                    "passivity",
                    models.CharField(
                        blank=True,
                        choices=[("Active", "Active"), ("Passive", "Passive")],
                        max_length=20,
                    ),
                ),
                (
                    "trigger_expl",
                    models.CharField(
                        choices=[
                            ("Distribution", "Distribution Source or Object"),
                            ("DistributionSource", "Distribution of Source Code"),
                            ("DistributionNonSource", "Distribution Non Source"),
                            ("NetworkAccess", "Network Access"),
                            ("InternalUse", "Internal Use"),
                        ],
                        default="Distribution",
                        max_length=40,
                    ),
                ),
                (
                    "trigger_mdf",
                    models.CharField(
                        choices=[
                            ("Altered", "Only if Modified"),
                            ("Unmodified", "Only if Not Modified"),
                            ("AlteredUnmodified", "Modified or Not"),
                        ],
                        default="AlteredUnmodified",
                        max_length=40,
                    ),
                ),
                (
                    "generic",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="cube.generic",
                    ),
                ),
                (
                    "license",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cube.license"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LicenseChoice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("expression_in", models.CharField(max_length=500)),
                ("expression_out", models.CharField(max_length=500)),
                (
                    "scope",
                    models.CharField(
                        blank=True,
                        max_length=128,
                        null=True,
                        help_text="Leave blank to apply for any scope",
                    ),
                ),
                (
                    "explanation",
                    models.TextField(blank=True, max_length=500, null=True),
                ),
                (
                    "component",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cube.component",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cube.product",
                    ),
                ),
                (
                    "release",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cube.release",
                    ),
                ),
                (
                    "version",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cube.version",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="generic",
            name="team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="cube.team",
            ),
        ),
        migrations.CreateModel(
            name="Derogation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "linking",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Aggregation", "Mere aggregation"),
                            ("Dynamic", "Dynamic Linking"),
                            ("Static", "Static Linking"),
                            ("Package", "Package Manager"),
                            ("Mingled", "Source code directly derived"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "scope",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("usage", "Only this usage"),
                            ("release", "The whole release"),
                            ("component", "Every usage of this component"),
                            ("linking", "Every usage with this same linking"),
                            ("scope", "Every usage with the same scope"),
                            (
                                "linkingscope",
                                "Every usage with the same scope AND the same linking",
                            ),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "justification",
                    models.TextField(blank=True, max_length=500, null=True),
                ),
                (
                    "license",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cube.license",
                        related_name="derogations",
                    ),
                ),
                (
                    "release",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cube.release",
                    ),
                ),
                (
                    "usage",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cube.usage",
                    ),
                ),
            ],
        ),
    ]
