#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django import forms

from cube.models import LicenseCuration, ExpressionValidation, LicenseChoice, Derogation
from cube.utils.licenses import explode_spdx_to_units


# Component only steps (curations and expression validation)


class BaseComponentDecisionForm(forms.ModelForm):
    ANY = "any"
    COMPONENT = "component"
    VERSION = "version"
    COMPONENT_VERSION_CHOICES = (
        (VERSION, "Apply to this version only"),
        (COMPONENT, "Apply to all component versions"),
        ("", "All components"),
    )

    component_version = forms.ChoiceField(
        label="Components or versions",
        choices=COMPONENT_VERSION_CHOICES,
        help_text="Rule will only apply to selected components",
    )

    def __init__(self, *args, **kwargs):
        self.usage = kwargs.pop("usage")
        super().__init__(*args, **kwargs)
        self.fields["component_version"].choices = (
            (self.VERSION, f"Only {self.usage.version}"),
            (self.COMPONENT, f"All {self.usage.version.component} versions"),
            (self.ANY, "All components"),
        )

    def save(self, **kwargs):
        if self.cleaned_data["component_version"] == self.COMPONENT:
            self.instance.component = self.usage.version.component
        elif self.cleaned_data["component_version"] == self.VERSION:
            self.instance.version = self.usage.version

        return super().save(**kwargs)

    class Meta:
        fields = (
            "expression_out",
            "component_version",
            "explanation",
        )


class CreateLicenseCurationForm(BaseComponentDecisionForm):
    expression_out = forms.CharField(
        label="Valid SPDX expression",
        help_text='Must use license identifiers from <a href="https://spdx.org/licenses/">SPDX License List</a> '
        "or <em>LicenseRef-[ref]</em> to refer other licenses.",
    )

    def save(self, **kwargs):
        if self.usage:
            self.instance.expression_in = self.usage.version.declared_license_expr
        return super().save(**kwargs)

    class Meta(BaseComponentDecisionForm.Meta):
        model = LicenseCuration


class CreateExpressionValidationForm(BaseComponentDecisionForm):
    expression_out = forms.CharField(
        label="Corrected SPDX expression",
        help_text="Must be same expression if correct, or another expression if some ANDs are actually ORs",
        widget=forms.TextInput(attrs={"size": 80}),
    )

    def clean(self):
        if explode_spdx_to_units(
            self.cleaned_data["expression_out"]
        ) == explode_spdx_to_units(self.usage.version.spdx_valid_license_expr):
            return

        self.add_error(
            "expression_out", "Expressions must use the same list of SPDX identifiers"
        )

    def save(self, **kwargs):
        self.instance.expression_in = self.usage.version.spdx_valid_license_expr
        return super().save(**kwargs)

    class Meta(BaseComponentDecisionForm.Meta):
        model = ExpressionValidation


# Usage steps (choices and derogations)


class BaseUsageConditionForm(BaseComponentDecisionForm):
    ANY = "any"
    PRODUCT = "product"
    RELEASE = "release"
    PRODUCT_RELEASE_CHOICES = (
        (RELEASE, "Apply to this release only"),
        (PRODUCT, "Apply to all product releases"),
        ("", "All products"),
    )
    USAGE_SCOPE = "usage"
    SCOPE_CHOICES = ((USAGE_SCOPE, "This usage scope"), (ANY, "Any scope"))

    product_release = forms.ChoiceField(
        label="Products or releases",
        choices=PRODUCT_RELEASE_CHOICES,
        help_text="Rule will only apply to selected products",
    )
    scope_choice = forms.ChoiceField(
        label="Rule will only apply to selected scope", choices=SCOPE_CHOICES
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change labels of fields depending on product and component  names
        self.fields["product_release"].choices = (
            (self.RELEASE, f"Only {self.usage.release}"),
            (self.PRODUCT, f"All {self.usage.release.product} releases"),
            (self.ANY, "All products"),
        )
        self.fields["scope_choice"].choices = (
            (self.USAGE_SCOPE, f'Only "{self.usage.scope}" scope'),
            (self.ANY, "Any scope"),
        )

    def save(self, **kwargs):
        if self.cleaned_data["product_release"] == self.PRODUCT:
            self.instance.product = self.usage.release.product
        elif self.cleaned_data["product_release"] == self.RELEASE:
            self.instance.release = self.usage.release

        if self.cleaned_data["scope_choice"] == self.USAGE_SCOPE:
            self.instance.scope = self.usage.scope

        return super().save(**kwargs)


class CreateLicenseChoiceForm(BaseUsageConditionForm):
    expression_out = forms.CharField(
        label="Final SPDX expression",
        help_text="The final expression of the license chosen for this usage",
        widget=forms.TextInput(attrs={"size": 80}),
    )

    def save(self, **kwargs):
        self.instance.expression_in = self.usage.version.effective_license
        return super().save(**kwargs)

    class Meta:
        model = LicenseChoice
        fields = (
            "expression_out",
            "product_release",
            "component_version",
            "scope_choice",
            "explanation",
        )


class CreateDerogationForm(BaseUsageConditionForm):
    USAGE_LINKING = "usage"
    LINKING_CHOICES = ((BaseUsageConditionForm.ANY, "Apply to any linking"),)

    linking_choice = forms.ChoiceField(choices=LINKING_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change labels of fields depending on usage linking
        if self.usage.linking:
            self.fields["linking_choice"].choices = (
                (self.USAGE_LINKING, f"Only {self.usage.get_linking_display()}"),
                (self.ANY, "Any linking"),
            )

    def save(self, **kwargs):
        if self.cleaned_data["linking_choice"] == self.USAGE_LINKING:
            self.instance.linking = self.usage.linking

        return super().save(**kwargs)

    class Meta:
        model = Derogation
        fields = (
            "product_release",
            "component_version",
            "linking_choice",
            "scope_choice",
            "justification",
        )
