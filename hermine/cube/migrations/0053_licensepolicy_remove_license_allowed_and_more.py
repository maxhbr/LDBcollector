import django.db.models.deletion
from django.contrib.auth.management import create_permissions
from django.db import migrations, models


def create_license_policies(apps, schema_editor):
    License = apps.get_model("cube", "License")
    LicensePolicy = apps.get_model("cube", "LicensePolicy")
    db_alias = schema_editor.connection.alias

    for license in License.objects.using(db_alias).all():
        LicensePolicy.objects.using(db_alias).create(
            license=license,
            status=license.status,
            categories=license.categories,
            allowed=license.allowed,
            allowed_explanation=license.allowed_explanation,
        )


def remove_license_policies(apps, schema_editor):
    License = apps.get_model("cube", "License")
    LicensePolicy = apps.get_model("cube", "LicensePolicy")
    db_alias = schema_editor.connection.alias

    for license_policy in LicensePolicy.objects.using(db_alias).all():
        license = license_policy.license
        license.status = license_policy.status
        license.categories = license_policy.categories
        license.allowed = license_policy.allowed
        license.allowed_explanation = license_policy.allowed_explanation
        license.save()


def update_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias

    app_config = apps.get_app_config("cube")
    app_config.models_module = True
    create_permissions(app_config, verbosity=0, using=db_alias)
    app_config.models_module = None

    # Update groups and user to give _licensepolicy permissions
    # to all who have already _license permissions
    view_license = Permission.objects.using(db_alias).get(codename="view_license")
    view_licensepolicy = Permission.objects.using(db_alias).get(
        codename="view_licensepolicy"
    )
    add_license = Permission.objects.using(db_alias).get(codename="add_license")
    add_licensepolicy = Permission.objects.using(db_alias).get(
        codename="add_licensepolicy"
    )
    change_license = Permission.objects.using(db_alias).get(codename="change_license")
    change_licensepolicy = Permission.objects.using(db_alias).get(
        codename="change_licensepolicy"
    )
    delete_license = Permission.objects.using(db_alias).get(codename="delete_license")
    delete_licensepolicy = Permission.objects.using(db_alias).get(
        codename="delete_licensepolicy"
    )
    for group in Group.objects.using(db_alias).all():
        if view_license in group.permissions.all():
            group.permissions.add(view_licensepolicy)
        if add_license in group.permissions.all():
            group.permissions.add(add_licensepolicy)
        if change_license in group.permissions.all():
            group.permissions.add(change_licensepolicy)
        if delete_license in group.permissions.all():
            group.permissions.add(delete_licensepolicy)
    for user in User.objects.using(db_alias).all():
        if view_license in user.user_permissions.all():
            user.user_permissions.add(view_licensepolicy)
        if add_license in user.user_permissions.all():
            user.user_permissions.add(add_licensepolicy)
        if change_license in user.user_permissions.all():
            user.user_permissions.add(change_licensepolicy)
        if delete_license in user.user_permissions.all():
            user.user_permissions.add(delete_licensepolicy)


class Migration(migrations.Migration):
    dependencies = [
        ("cube", "0052_remove_license_autoupgrade_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="LicensePolicy",
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
                    "license",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="policy",
                        to="cube.license",
                    ),
                ),
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
                        verbose_name="Review status",
                    ),
                ),
                ("categories", models.CharField(blank=True, max_length=200)),
                (
                    "allowed",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("always", "Always allowed"),
                            ("never", "Never allowed"),
                            ("context", "Allowed depending on context"),
                            ("notfoss", "Out of FOSS Policy"),
                            ("", "Not reviewed yet"),
                        ],
                        max_length=20,
                        verbose_name="OSS Policy",
                    ),
                ),
                (
                    "allowed_explanation",
                    models.TextField(
                        blank=True,
                        max_length=1500,
                        verbose_name="OSS Policy explanation",
                    ),
                ),
            ],
            options={
                "verbose_name": "License policy",
                "verbose_name_plural": "License policies",
            },
        ),
        migrations.RunPython(create_license_policies, remove_license_policies),
        migrations.RemoveField(
            model_name="license",
            name="allowed",
        ),
        migrations.RemoveField(
            model_name="license",
            name="allowed_explanation",
        ),
        migrations.RemoveField(
            model_name="license",
            name="categories",
        ),
        migrations.RemoveField(
            model_name="license",
            name="status",
        ),
        migrations.RunPython(update_permissions, migrations.RunPython.noop),
    ]
