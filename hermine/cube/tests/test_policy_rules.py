#  SPDX-FileCopyrightText: 2023 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.test import TestCase
from semantic_version import SimpleSpec

from cube.models import Release, LicenseCuration, LicenseChoice, License, Derogation
from cube.utils.release_validation import (
    apply_curations,
    propagate_choices,
    check_licenses_against_policy,
)


class LicenseCurationTestCase(TestCase):
    fixtures = ["test_data.json"]
    expressions = {
        "expression_in": "LicenseRef-FakeLicense OR AND LicenseRef-FakeLicense-Permissive",
        "expression_out": "LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
    }

    def setUp(self):
        self.release = Release.objects.get(id=1)

    def apply_curations(self):
        apply_curations(self.release)

    def assert_curation_applied(self):
        self.assertEqual(
            "LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
            self.release.usage_set.last().version.corrected_license,
        )

    def assert_curation_not_applied(self):
        self.assertEqual(
            "",
            self.release.usage_set.last().version.corrected_license,
        )

    def test_no_curations(self):
        self.apply_curations()
        self.assert_curation_not_applied()

    def test_all_version_component_curation(self):
        version = self.release.usage_set.last().version
        LicenseCuration.objects.create(component=version.component, **self.expressions)
        self.apply_curations()
        self.assert_curation_applied()

    def test_single_version_curation(self):
        version = self.release.usage_set.last().version
        LicenseCuration.objects.create(version=version, **self.expressions)
        self.apply_curations()
        self.assert_curation_applied()

    def test_single_other_version_curation(self):
        version = self.release.usage_set.first().version
        LicenseCuration.objects.create(version=version, **self.expressions)
        self.apply_curations()
        self.assert_curation_not_applied()

    def test_conflicting_expressions_out(self):
        version = self.release.usage_set.last().version
        LicenseCuration.objects.create(version=version, **self.expressions)
        LicenseCuration.objects.create(
            version=version,
            expression_in=self.expressions["expression_in"],
            expression_out="MIT",
        )
        self.apply_curations()
        self.assert_curation_not_applied()

    def test_conflicting_single_and_all_versions(self):
        version = self.release.usage_set.last().version
        LicenseCuration.objects.create(
            version=version,
            expression_in=self.expressions["expression_in"],
            expression_out="MIT",
        )
        LicenseCuration.objects.create(component=version.component, **self.expressions)
        self.apply_curations()
        self.assert_curation_not_applied()

    def test_matching_version_spec(self):
        version = self.release.usage_set.last().version
        LicenseCuration.objects.create(
            component=version.component,
            version_constraint=SimpleSpec(">=2.0.0"),
            **self.expressions
        )
        self.apply_curations()
        self.assert_curation_applied()

    def test_not_matching_version_spec(self):
        version = self.release.usage_set.last().version
        LicenseCuration.objects.create(
            component=version.component,
            version_constraint=SimpleSpec(">=3.0.0"),
            **self.expressions
        )
        self.apply_curations()
        self.assert_curation_not_applied()


class LicenseChoiceTestCase(TestCase):
    fixtures = ["test_data.json"]
    expressions = {
        "expression_in": "LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
        "expression_out": "LicenseRef-FakeLicense-Permissive",
    }

    def setUp(self):
        self.release = Release.objects.get(id=1)
        version = self.release.usage_set.last().version
        LicenseCuration.objects.create(
            component=version.component,
            expression_in="LicenseRef-FakeLicense OR AND LicenseRef-FakeLicense-Permissive",
            expression_out="LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
        )
        apply_curations(self.release)

    def propagate_choices(self):
        propagate_choices(self.release)

    def assert_choice_propagated(self):
        self.assertEqual(
            "LicenseRef-FakeLicense-Permissive",
            self.release.usage_set.last().license_expression,
        )

    def assert_choice_did_not_propagate(self):
        self.assertEqual(
            "",
            self.release.usage_set.last().license_expression,
        )

    def test_no_choices(self):
        self.propagate_choices()
        self.assert_choice_did_not_propagate()

    def test_all_component_choice(self):
        LicenseChoice.objects.create(**self.expressions)
        self.propagate_choices()
        self.assert_choice_propagated()

    def test_all_version_component_choice(self):
        version = self.release.usage_set.last().version
        LicenseChoice.objects.create(component=version.component, **self.expressions)
        self.propagate_choices()
        self.assert_choice_propagated()

    def test_single_version_choice(self):
        version = self.release.usage_set.last().version
        LicenseChoice.objects.create(version=version, **self.expressions)
        self.propagate_choices()
        self.assert_choice_propagated()

    def test_single_other_version_choice(self):
        version = self.release.usage_set.first().version
        LicenseChoice.objects.create(version=version, **self.expressions)
        self.propagate_choices()
        self.assert_choice_did_not_propagate()

    def test_conflicting_expressions_out(self):
        version = self.release.usage_set.last().version
        LicenseChoice.objects.create(version=version, **self.expressions)
        LicenseChoice.objects.create(
            version=version,
            expression_in=self.expressions["expression_in"],
            expression_out="LicenseRef-FakeLicense",
        )
        self.propagate_choices()
        self.assert_choice_did_not_propagate()

    def test_conflicting_single_and_all_versions(self):
        version = self.release.usage_set.last().version
        LicenseChoice.objects.create(
            version=version,
            expression_in=self.expressions["expression_in"],
            expression_out="LicenseRef-FakeLicense",
        )
        LicenseChoice.objects.create(component=version.component, **self.expressions)
        self.propagate_choices()
        self.assert_choice_did_not_propagate()

    def test_matching_version_spec(self):
        version = self.release.usage_set.last().version
        LicenseChoice.objects.create(
            component=version.component,
            version_constraint=SimpleSpec(">=2.0.0"),
            **self.expressions
        )
        self.propagate_choices()
        self.assert_choice_propagated()

    def test_not_matching_version_spec(self):
        version = self.release.usage_set.last().version
        LicenseChoice.objects.create(
            component=version.component,
            version_constraint=SimpleSpec(">=3.0.0"),
            **self.expressions
        )
        self.propagate_choices()
        self.assert_choice_did_not_propagate()


class LicensePolicyTestCase(TestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        self.release = Release.objects.get(id=1)
        version = self.release.usage_set.last().version
        LicenseCuration.objects.create(
            component=version.component,
            expression_in="LicenseRef-FakeLicense OR AND LicenseRef-FakeLicense-Permissive",
            expression_out="LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
        )
        apply_curations(self.release)
        LicenseChoice.objects.create(
            expression_in="LicenseRef-FakeLicense OR LicenseRef-FakeLicense-Permissive",
            expression_out="LicenseRef-FakeLicense-Permissive",
        )
        propagate_choices(self.release)

    def test_unknown(self):
        never, context, unknown, lic, derogations = check_licenses_against_policy(
            self.release
        ).values()
        self.assertEqual(len(unknown), 2)  # LicenseRef-FakeLicense-Permissive
        self.assertEqual(len(context), 0)
        self.assertEqual(len(never), 0)
        self.assertEqual(len(lic), 1)
        self.assertEqual(len(derogations), 0)
        self.assertEqual(lic.pop().spdx_id, "LicenseRef-FakeLicense-Permissive")

    def test_never(self):
        License.objects.filter(spdx_id="LicenseRef-FakeLicense-Permissive").update(
            allowed=License.ALLOWED_NEVER
        )
        never, context, unknown, lic, derogations = check_licenses_against_policy(
            self.release
        ).values()
        self.assertEqual(len(unknown), 0)
        self.assertEqual(len(context), 0)
        self.assertEqual(len(never), 2)
        self.assertEqual(len(lic), 1)
        self.assertEqual(len(derogations), 0)
        self.assertEqual(lic.pop().spdx_id, "LicenseRef-FakeLicense-Permissive")

    def test_allowed(self):
        License.objects.filter(spdx_id="LicenseRef-FakeLicense-Permissive").update(
            allowed=License.ALLOWED_ALWAYS
        )
        never, context, unknown, lic, derogations = check_licenses_against_policy(
            self.release
        ).values()
        self.assertEqual(len(unknown), 0)
        self.assertEqual(len(context), 0)
        self.assertEqual(len(never), 0)
        self.assertEqual(len(lic), 1)
        self.assertEqual(len(derogations), 0)
        self.assertEqual(lic.pop().spdx_id, "LicenseRef-FakeLicense-Permissive")

    def test_release_derogation(self):
        Derogation.objects.create(
            release=self.release,
            license=License.objects.get(spdx_id="LicenseRef-FakeLicense-Permissive"),
        )
        never, context, unknown, lic, derogations = check_licenses_against_policy(
            self.release
        ).values()
        self.assertEqual(len(unknown), 0)
        self.assertEqual(len(context), 0)
        self.assertEqual(len(never), 0)
        self.assertEqual(len(lic), 1)
        self.assertEqual(len(derogations), 1)

    def test_single_version_derogation(self):
        Derogation.objects.create(
            version=self.release.usage_set.last().version,
            license=License.objects.get(spdx_id="LicenseRef-FakeLicense-Permissive"),
        )
        never, context, unknown, lic, derogations = check_licenses_against_policy(
            self.release
        ).values()
        self.assertEqual(
            len(unknown), 1
        )  # The version which does not have a derogation
        self.assertEqual(len(context), 0)
        self.assertEqual(len(never), 0)
        self.assertEqual(len(lic), 1)
        self.assertEqual(len(derogations), 1)

    def test_component_derogation(self):
        Derogation.objects.create(
            component=self.release.usage_set.last().version.component,
            license=License.objects.get(spdx_id="LicenseRef-FakeLicense-Permissive"),
        )
        never, context, unknown, lic, derogations = check_licenses_against_policy(
            self.release
        ).values()
        self.assertEqual(len(unknown), 0)
        self.assertEqual(len(context), 0)
        self.assertEqual(len(never), 0)
        self.assertEqual(len(lic), 1)
        self.assertEqual(len(derogations), 1)

    def test_derogation_for_never_allowed(self):
        Derogation.objects.create(
            component=self.release.usage_set.last().version.component,
            license=License.objects.get(spdx_id="LicenseRef-FakeLicense-Permissive"),
        )
        License.objects.filter(spdx_id="LicenseRef-FakeLicense-Permissive").update(
            allowed=License.ALLOWED_NEVER
        )
        never, context, unknown, lic, derogations = check_licenses_against_policy(
            self.release
        ).values()
        self.assertEqual(len(unknown), 0)
        self.assertEqual(len(context), 0)
        self.assertEqual(len(never), 0)
        self.assertEqual(len(lic), 1)
        self.assertEqual(len(derogations), 1)
        self.assertEqual(lic.pop().spdx_id, "LicenseRef-FakeLicense-Permissive")

    def test_matching_version_spec_derogation(self):
        Derogation.objects.create(
            component=self.release.usage_set.last().version.component,
            version_constraint=SimpleSpec(">=1.0.0"),
            license=License.objects.get(spdx_id="LicenseRef-FakeLicense-Permissive"),
        )
        never, context, unknown, lic, derogations = check_licenses_against_policy(
            self.release
        ).values()
        self.assertEqual(len(unknown), 0)
        self.assertEqual(len(context), 0)
        self.assertEqual(len(never), 0)
        self.assertEqual(len(lic), 1)
        self.assertEqual(len(derogations), 1)

    def test_single_matching_version_spec_derogation(self):
        Derogation.objects.create(
            component=self.release.usage_set.last().version.component,
            version_constraint=SimpleSpec(">=2.0.0"),
            license=License.objects.get(spdx_id="LicenseRef-FakeLicense-Permissive"),
        )
        never, context, unknown, lic, derogations = check_licenses_against_policy(
            self.release
        ).values()
        self.assertEqual(len(unknown), 1)
        self.assertEqual(len(context), 0)
        self.assertEqual(len(never), 0)
        self.assertEqual(len(lic), 1)
        self.assertEqual(len(derogations), 1)
