# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from urllib.parse import quote

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework.views import APIView

from cube import urls
from cube.forms.release_validation import (
    CreateLicenseCurationForm,
    CreateAndsValidationForm,
    CreateLicenseChoiceForm,
)
from cube.models import (
    Compatibility,
    Generic,
    LicenseCuration,
    LicenseChoice,
    LicensePolicy,
    Exploitation,
    Obligation,
    Release,
    Version,
    Usage,
    License,
)
from .mixins import ForceLoginMixin


class UnauthenticatedTestCase(TestCase):
    fixtures = ["test_data.json"]
    urls = [
        reverse("cube:dashboard"),
        reverse("cube:product_list"),
        reverse("cube:product_detail", kwargs={"pk": 1}),
        reverse("cube:component_list"),
        reverse("cube:component_detail", kwargs={"pk": 2}),
        *[
            reverse(f"cube:release_validation_step_{step}", kwargs={"pk": 1})
            for step in range(1, 7)
        ],
        reverse("cube:release_summary", kwargs={"pk": 1}),
        reverse("cube:release_bom", kwargs={"release_pk": 1}),
        reverse("cube:release_bom_export", kwargs={"pk": 1}),
        reverse("cube:license_list"),
        reverse("cube:license_detail", kwargs={"pk": 1}),
        reverse("cube:generic_list"),
        reverse("cube:generic_detail", kwargs={"pk": 1}),
    ]

    def test_protected_views(self):
        for url in self.urls:
            res = self.client.get(url)
            self.assertRedirects(
                res, reverse("login") + "?next=" + quote(url, safe="/")
            )
        self.client.force_login(User.objects.get(username="admin"))
        for url in self.urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200)

    def test_all_views_have_permissions(self):
        for view in urls.urlpatterns:
            if (
                hasattr(view, "view_class")
                and not issubclass(view.view_class, APIView)
                and not issubclass(view.view_class, PermissionRequiredMixin)
            ):
                self.assertNotIn(view.view_class.__name__, ("IndexView", "AboutView"))


class ProductViewsTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_products_view(self):
        url = reverse("cube:product_list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "test_product")

    def test_product_detail_view(self):
        url = reverse("cube:product_detail", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "This is for testing purpose")  # product description


class ComponentViewsTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_components_view(self):
        url = reverse("cube:component_list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "3rd Party Components")
        self.assertContains(res, "test_component_alpha")  # component name

    def test_component_detail_view(self):
        url = reverse("cube:component_detail", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "test_component_alpha")  # component name
        self.assertContains(res, "test_product")  # product in which component is used


class LicenseViewsTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_license_details_display_obligations(self):
        res = self.client.get(reverse("cube:license_detail", args=[1]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Test License Distribution Unmodified")


class ReleaseViewsTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_release_summary_with_multiple_exploitation_choice(self):
        url = reverse("cube:release_summary", kwargs={"pk": 1})
        Exploitation.objects.create(release_id=1, scope="back")
        Exploitation.objects.create(release_id=1, scope="front")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_release_validation_view(self):
        url = reverse("cube:release_validation_step_1", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Release: 1.0")  # release number

    def test_release_bom_view(self):
        url = reverse("cube:release_bom", kwargs={"release_pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(
            res, "test_component_alpha"
        )  # test component alpha is used in release 1

    def test_create_license_curation(self):
        url = reverse("cube:release_licensecuration_create", args=[1])
        res = self.client.post(
            url,
            {
                "expression_out": "MIT",
                "component_version": CreateLicenseCurationForm.ANY,
            },
        )
        self.assertRedirects(res, reverse("cube:release_validation_step_1", args=[1]))
        self.assertEqual(LicenseCuration.objects.all().count(), 1)
        self.assertEqual(LicenseCuration.objects.first().author, self.user)
        self.assertEqual(LicenseChoice.objects.all().count(), 0)

    def test_create_license_curation_version_scope(self):
        """Test that component_version=VERSION sets version field"""
        url = reverse("cube:release_licensecuration_create", args=[1])
        res = self.client.post(
            url,
            {
                "expression_out": "MIT",
                "component_version": CreateLicenseCurationForm.VERSION,
            },
        )
        self.assertRedirects(res, reverse("cube:release_validation_step_1", args=[1]))
        curation = LicenseCuration.objects.first()
        self.assertIsNotNone(curation.version)
        self.assertIsNone(curation.component)

    def test_create_license_curation_component_scope(self):
        """Test that component_version=COMPONENT sets component field"""
        url = reverse("cube:release_licensecuration_create", args=[1])
        res = self.client.post(
            url,
            {
                "expression_out": "MIT",
                "component_version": CreateLicenseCurationForm.COMPONENT,
            },
        )
        self.assertRedirects(res, reverse("cube:release_validation_step_1", args=[1]))
        curation = LicenseCuration.objects.first()
        self.assertIsNone(curation.version)
        self.assertIsNotNone(curation.component)

    def test_create_license_curation_constraint_scope(self):
        """Test that component_version=CONSTRAINT sets component field"""
        url = reverse("cube:release_licensecuration_create", args=[1])
        res = self.client.post(
            url,
            {
                "expression_out": "MIT",
                "component_version": CreateLicenseCurationForm.CONSTRAINT,
                "version_constraint": ">=1.0.0",
            },
        )
        self.assertRedirects(res, reverse("cube:release_validation_step_1", args=[1]))
        curation = LicenseCuration.objects.first()
        self.assertIsNone(curation.version)
        self.assertIsNotNone(curation.component)
        self.assertEqual(str(curation.version_constraint), ">=1.0.0")

    def test_create_ands_validation_version_scope(self):
        Version.objects.filter(pk=2).update(
            spdx_valid_license_expr="LicenseRef-FakeLicense AND LicenseRef-FakeLicense-Permissive"
        )
        """Test that component_version=VERSION sets version field on ands validation"""
        url = reverse("cube:release_andsvalidation_create", args=[2])
        res = self.client.post(
            url,
            {
                "expression_out": "LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
                "component_version": CreateAndsValidationForm.VERSION,
            },
        )
        self.assertRedirects(res, reverse("cube:release_validation_step_2", args=[1]))
        curation = LicenseCuration.objects.first()
        self.assertIsNotNone(curation.version)
        self.assertIsNone(curation.component)

    def test_create_ands_validation_component_scope(self):
        Version.objects.filter(pk=2).update(
            spdx_valid_license_expr="LicenseRef-FakeLicense AND LicenseRef-FakeLicense-Permissive"
        )
        """Test that component_version=COMPONENT sets component field on ands validation"""
        url = reverse("cube:release_andsvalidation_create", args=[2])
        res = self.client.post(
            url,
            {
                "expression_out": "LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
                "component_version": CreateAndsValidationForm.COMPONENT,
            },
        )
        self.assertRedirects(res, reverse("cube:release_validation_step_2", args=[1]))
        curation = LicenseCuration.objects.first()
        self.assertIsNone(curation.version)
        self.assertIsNotNone(curation.component)

    def test_create_ands_validation_constraint_scope(self):
        Version.objects.filter(pk=2).update(
            spdx_valid_license_expr="LicenseRef-FakeLicense AND LicenseRef-FakeLicense-Permissive"
        )
        """Test that component_version=CONSTRAINT sets component field on ands validation"""
        url = reverse("cube:release_andsvalidation_create", args=[2])
        res = self.client.post(
            url,
            {
                "expression_out": "LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
                "component_version": CreateAndsValidationForm.CONSTRAINT,
                "version_constraint": ">=1.0.0",
            },
        )
        self.assertRedirects(res, reverse("cube:release_validation_step_2", args=[1]))
        curation = LicenseCuration.objects.first()
        self.assertIsNone(curation.version)
        self.assertIsNotNone(curation.component)
        self.assertEqual(str(curation.version_constraint), ">=1.0.0")

    def test_create_licence_choice_rule(self):
        url = reverse("cube:release_licensechoice_create", args=[1])
        self.client.post(
            url,
            {
                "expression_out": "LicenseRef-FakeLicense-Permissive",
                "product_release": CreateLicenseChoiceForm.PRODUCT,
                "component_version": CreateLicenseChoiceForm.COMPONENT,
                "exploitation_choice": CreateLicenseChoiceForm.ANY,
                "scope_choice": CreateLicenseChoiceForm.ANY,
            },
        )
        self.assertEqual(
            LicenseChoice.objects.first().expression_in,
            "LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
        )


class ExportSBOMTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_export_simple_sbom(self):
        url = reverse("cube:release_bom_export", args=[1])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "name,version")
        self.assertContains(res, "LicenseRef-FakeLicense OR AND")


class LicenseDeleteButtonVisibilityTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        super().setUp()
        # Ensure we start with a clean unused license for visibility tests
        self.license = License.objects.get(pk=1)
        # Sanity: the license should not be linked to any usage by default
        # (fixtures don't link licenses via Usage.licenses_chosen)
        self.assertFalse(self.license.usage_set.exists())

    def test_delete_button_visible_when_unused_and_user_has_permission(self):
        url = reverse("cube:license_detail", kwargs={"pk": self.license.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        # Button should be visible as admin has delete permission and license is unused
        self.assertContains(
            res,
            reverse("cube:license_delete", kwargs={"pk": self.license.pk}),
        )

    def test_delete_button_hidden_when_license_is_used(self):
        # Mark the license as used by adding it to an existing Usage
        usage = Usage.objects.get(pk=1)
        usage.licenses_chosen.add(self.license)

        url = reverse("cube:license_detail", kwargs={"pk": self.license.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        # Delete button should not be present when license is used
        self.assertNotContains(
            res,
            reverse("cube:license_delete", kwargs={"pk": self.license.pk}),
        )


class LicenseDeleteViewBehaviorTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_get_delete_for_used_license_returns_404(self):
        lic = License.objects.get(pk=1)
        usage = Usage.objects.get(pk=1)
        usage.licenses_chosen.add(lic)

        url = reverse("cube:license_delete", kwargs={"pk": lic.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

    def test_get_and_post_delete_for_unused_license(self):
        # Create a brand new unused license
        lic = License.objects.create(
            spdx_id="LicenseRef-Temp-DeleteTest",
            long_name="Temporary License For Delete Test",
        )
        # Sanity: no usage should point to it
        self.assertFalse(lic.usage_set.exists())

        # GET should render the confirmation page
        url = reverse("cube:license_delete", kwargs={"pk": lic.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Delete license")

        # POST should delete and redirect to the list
        res = self.client.post(url, follow=False)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("cube:license_list"))
        # Object is deleted
        self.assertFalse(License.objects.filter(pk=lic.pk).exists())


class LicenseDeletePermissionTestCase(TestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        # Create a regular user without delete permissions
        self.user = User.objects.create_user(
            username="regular_user", email="u@example.com", password="pass"
        )
        self.client.force_login(self.user)
        # Create an unused license
        self.lic = License.objects.create(
            spdx_id="LicenseRef-NoPerm-DeleteTest", long_name="NoPerm License"
        )

    def test_user_without_permission_cannot_access_delete_view(self):
        url = reverse("cube:license_delete", kwargs={"pk": self.lic.pk})
        res = self.client.get(url)
        # Depending on settings, PermissionRequiredMixin will either redirect to login (302)
        # or respond with 403. Accept either to keep test robust across configs.
        self.assertIn(res.status_code, (302, 403))

        # If redirected, ensure it's towards login
        if res.status_code == 302:
            self.assertIn(reverse("login"), res.url)

        # Grant permission and try again → should be 200 on GET
        perm = Permission.objects.get(codename="delete_license")
        self.user.user_permissions.add(perm)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)


class LicenseListViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_license_list(self):
        url = reverse("cube:license_list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "LicenseRef-FakeLicense")

    def test_license_list_filter(self):
        url = reverse("cube:license_list") + "?spdx_id=FakeLicense"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)


class LicenseCreateViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_get_create_form(self):
        url = reverse("cube:license_create")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_license(self):
        url = reverse("cube:license_create")
        res = self.client.post(
            url,
            {
                "spdx_id": "LicenseRef-NewTest-1.0",
                "long_name": "New Test License",
                "copyleft": "None",
                "foss": "Yes",
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertTrue(
            License.objects.filter(spdx_id="LicenseRef-NewTest-1.0").exists()
        )


class LicenseUpdateViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_get_update_form(self):
        url = reverse("cube:license_update", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_update_license(self):
        url = reverse("cube:license_update", kwargs={"pk": 1})
        res = self.client.post(
            url,
            {
                "spdx_id": "LicenseRef-FakeLicense",
                "long_name": "Updated Name",
                "copyleft": "Strong",
                "foss": "Yes",
            },
        )
        self.assertEqual(res.status_code, 302)
        lic = License.objects.get(pk=1)
        self.assertEqual(lic.long_name, "Updated Name")

    def test_duplicate_license(self):
        url = reverse("cube:license_update", kwargs={"pk": 1})
        original_count = License.objects.count()
        obligation_count = Obligation.objects.filter(license_id=1).count()
        res = self.client.post(
            url,
            {
                "spdx_id": "LicenseRef-FakeLicense-Copy",
                "long_name": "Fake License (copy)",
                "copyleft": "None",
                "foss": "Yes",
                "duplicate": "1",
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(License.objects.count(), original_count + 1)
        copy = License.objects.get(spdx_id="LicenseRef-FakeLicense-Copy")
        self.assertEqual(copy.obligation_set.count(), obligation_count)


class LicensePolicyUpdateViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_get_policy_form(self):
        url = reverse("cube:license_update_policy", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_update_policy(self):
        url = reverse("cube:license_update_policy", kwargs={"pk": 1})
        res = self.client.post(
            url,
            {
                "status": "Checked",
                "categories": "test",
                "allowed": "always",
                "allowed_explanation": "Allowed for testing",
            },
        )
        self.assertRedirects(res, reverse("cube:license_detail", args=[1]))
        policy = LicensePolicy.objects.get(license_id=1)
        self.assertEqual(policy.allowed, "always")


class LicensePrintViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_print_license_odt(self):
        url = reverse("cube:license_print", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "application/vnd.oasis.opendocument.text")
        self.assertIn("attachment", res["Content-Disposition"])


class ObligationCRUDViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_create_obligation(self):
        url = reverse("cube:obligation_create", kwargs={"license_pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            url,
            {
                "name": "New Test Obligation",
                "verbatim": "Test verbatim text",
                "passivity": "Active",
                "trigger_expl": "DistributionSourceDistributionNonSource",
                "trigger_mdf": "AlteredUnmodified",
            },
        )
        self.assertEqual(res.status_code, 302)
        obligation = Obligation.objects.get(name="New Test Obligation")
        self.assertEqual(obligation.license_id, 1)

    def test_update_obligation(self):
        obligation = Obligation.objects.filter(license_id=1).first()
        url = reverse("cube:obligation_update", kwargs={"pk": obligation.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            url,
            {
                "name": obligation.name,
                "verbatim": "Updated verbatim",
                "passivity": "Passive",
                "trigger_expl": obligation.trigger_expl,
                "trigger_mdf": obligation.trigger_mdf,
            },
        )
        self.assertRedirects(res, reverse("cube:license_detail", args=[1]))
        obligation.refresh_from_db()
        self.assertEqual(obligation.verbatim, "Updated verbatim")

    def test_delete_obligation(self):
        obligation = Obligation.objects.filter(license_id=1).first()
        url = reverse("cube:obligation_delete", kwargs={"pk": obligation.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Obligation.objects.filter(pk=obligation.pk).exists())


class ObligationsOrphansViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_orphan_obligations_list(self):
        url = reverse("cube:obligations_orphans")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)


class CompatibilityCRUDViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_create_and_delete_compatibility(self):
        # Create a second license to set up compatibility
        lic2 = License.objects.create(
            spdx_id="LicenseRef-Compat-Target",
            long_name="Compatibility Target License",
        )

        # Create
        url = reverse("cube:compatibility_create", kwargs={"license_pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            url,
            {
                "to_license": lic2.pk,
                "direction": "A",
            },
        )
        self.assertEqual(res.status_code, 302)
        compat = Compatibility.objects.get(from_license_id=1, to_license=lic2)
        self.assertEqual(compat.direction, "A")

        # Delete
        url = reverse(
            "cube:compatibility_delete",
            kwargs={"license_pk": 1, "pk": compat.pk},
        )
        res = self.client.post(url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Compatibility.objects.filter(pk=compat.pk).exists())


class GenericCRUDViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_generic_list(self):
        url = reverse("cube:generic_list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_generic_detail(self):
        url = reverse("cube:generic_detail", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_generic(self):
        url = reverse("cube:generic_create")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            url,
            {
                "name": "New Test Generic",
                "description": "Test description",
                "in_core": True,
                "metacategory": "Mentions",
                "passivity": "Active",
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Generic.objects.filter(name="New Test Generic").exists())

    def test_update_generic(self):
        url = reverse("cube:generic_update", kwargs={"pk": 1})
        generic = Generic.objects.get(pk=1)
        res = self.client.post(
            url,
            {
                "name": generic.name,
                "description": "Updated description",
                "in_core": generic.in_core,
                "metacategory": generic.metacategory,
                "passivity": generic.passivity,
            },
        )
        self.assertEqual(res.status_code, 302)
        generic.refresh_from_db()
        self.assertEqual(generic.description, "Updated description")


class ReleaseDeleteViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_delete_release(self):
        release = Release.objects.get(pk=2)
        product_pk = release.product_id
        url = reverse("cube:release_delete", kwargs={"pk": 2})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(url)
        self.assertRedirects(
            res, reverse("cube:product_detail", kwargs={"pk": product_pk})
        )
        self.assertFalse(Release.objects.filter(pk=2).exists())


class ReleaseObligationsViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_release_obligations(self):
        url = reverse("cube:release_obligations", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)


class ReleaseGenericViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_release_generic(self):
        url = reverse(
            "cube:release_generic",
            kwargs={"release_pk": 1, "generic_id": 1},
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)


class UsageCRUDViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_get_create_usage_form(self):
        url = reverse("cube:usage_create", kwargs={"release_pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_update_usage(self):
        usage = Usage.objects.get(pk=1)
        url = reverse("cube:usage_update", kwargs={"pk": usage.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_delete_usage(self):
        usage = Usage.objects.get(pk=1)
        url = reverse("cube:usage_delete", kwargs={"pk": usage.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Usage.objects.filter(pk=usage.pk).exists())


class ScopeUsagesDeleteViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_scope_usages_delete(self):
        url = reverse("cube:scope_usages_delete", kwargs={"release_pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Usage.objects.filter(release_id=1).count(), 0)


class ReleaseUpdateViewTestCase(ForceLoginMixin, TestCase):
    fixtures = ["test_data.json"]

    def test_get_release_update_form(self):
        url = reverse("cube:release_update", kwargs={"pk": 1})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
