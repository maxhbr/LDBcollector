# Generated by Django 4.1.1 on 2022-12-13 14:23
from django.db.models import Subquery, OuterRef

import cube.utils.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def merge_curations(app, schema_editor):
    UsageDecision = app.get_model("cube", "UsageDecision")
    LicenseCuration = app.get_model("cube", "LicenseCuration")
    db_alias = schema_editor.connection.alias

    # copy LicenseCuration and ExpressionValidation (proxy of UsageDecision) into new table for LicenseCuration

    LicenseCuration.objects.using(db_alias).bulk_create(
        LicenseCuration(
            created=curation.created,
            updated=curation.updated,
            author=curation.author,
            component=curation.component,
            version=curation.version,
            declared_expression="",
            expression_in=curation.expression_in,
            expression_out=curation.expression_out,
            explanation=curation.explanation,
        )
        for curation in UsageDecision.objects.using(db_alias).exclude(
            decision_type="choice"
        )
    )

    # merged chained curations

    for curation in (
        LicenseCuration.objects.using(db_alias)
        .annotate(
            chain=Subquery(
                LicenseCuration.objects.using(db_alias)
                .filter(
                    component=OuterRef("component"),
                    version=OuterRef("version"),
                    expression_in=OuterRef("expression_out"),
                )
                .values("pk")
            )
        )
        .exclude(chain=None)
    ):
        for chain_pk in curation.chain:
            chained_curation = LicenseCuration.objects.using(db_alias).get(pk=chain_pk)
            chained_curation.expression_in = curation.expression_in
            chained_curation.explanation = (
                f"This curation was automatically merged out of two chained_curationed curations. "
                f"Explanation 1 : {curation.explanation}. Explanation 2 : {chained_curation.explanation}"
            )
            chained_curation.save()
        curation.delete()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cube", "0030_derogation_author_derogation_created_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="version",
            unique_together={("component", "version_number")},
        ),
        migrations.DeleteModel(
            name="LicenseCuration",
        ),
        migrations.DeleteModel(
            name="ExpressionValidation",
        ),
        migrations.DeleteModel(
            name="LicenseChoice",
        ),
        migrations.CreateModel(
            name="LicenseCuration",
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
                ("created", models.DateTimeField()),
                ("updated", models.DateTimeField()),
                (
                    "declared_expression",
                    models.CharField(
                        blank=True,
                        help_text="The declared expression before any curation (used only for curation exports)",
                        max_length=500,
                    ),
                ),
                (
                    "expression_in",
                    models.CharField(
                        blank=True,
                        help_text="The exact expression which must be changed",
                        max_length=500,
                    ),
                ),
                (
                    "expression_out",
                    models.CharField(
                        help_text="The expression which will replace `expression_in`",
                        max_length=500,
                        validators=[cube.utils.validators.validate_spdx_expression],
                    ),
                ),
                (
                    "explanation",
                    models.TextField(blank=True, max_length=500, null=True),
                ),
                (
                    "author",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
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
        migrations.RunPython(merge_curations),
        migrations.RenameModel("UsageDecision", "LicenseChoice"),
        migrations.AlterField(
            model_name="licensechoice",
            name="expression_in",
            field=models.CharField(
                help_text="The exact expression which must be changed", max_length=500
            ),
        ),
        migrations.AlterField(
            model_name="licensechoice",
            name="expression_out",
            field=models.CharField(
                help_text="The final license expression chosen. Can still contains ANDs, and even ORs if you want to comply with all licenses and let the end user choose.",
                max_length=500,
                validators=[
                    cube.utils.validators.validate_spdx_expression,
                ],
                verbose_name="Final SPDX expression",
            ),
        ),
        migrations.AlterModelOptions(
            name="licensechoice",
            options={
                "verbose_name": "License choice rule",
                "verbose_name_plural": "License choice rules",
            },
        ),
        migrations.RemoveField(
            model_name="licensechoice",
            name="decision_type",
        ),
        migrations.AlterField(
            model_name="licensecuration",
            name="created",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="licensecuration",
            name="updated",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="version",
            name="corrected_license",
            field=models.CharField(
                blank=True,
                help_text="Final license expression used in legal evaluation (required when validated expression is ambiguous or empty)",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="version",
            name="spdx_valid_license_expr",
            field=models.CharField(
                blank=True,
                help_text="License expression concluded by analyzing tool (e.g. ORT)",
                max_length=200,
                validators=[cube.utils.validators.validate_spdx_expression],
            ),
        ),
    ]
