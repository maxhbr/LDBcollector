#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django import forms

from cube.models import LicenseCuration, LicenseChoice, Derogation, Category
from cube.utils.spdx import get_ands_corrections, explode_spdx_to_units


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


class CreateAndsValidationForm(BaseComponentDecisionForm):
    expression_out = forms.ChoiceField(
        label="Corrected SPDX expression",
        help_text="Must be same expression if correct, or another expression if some ANDs are actually ORs",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        corrections = get_ands_corrections(self.usage.version.spdx_valid_license_expr)
        self.fields["expression_out"].choices = (
            (choice, choice) for choice in corrections
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
        model = LicenseCuration


# Usage steps (choices and derogations)


class BaseUsageConditionForm(BaseComponentDecisionForm):
    ANY = "any"
    PRODUCT = "product"
    RELEASE = "release"
    CATEGORY = "category"
    USAGE = "usage"
    PRODUCT_RELEASE_CHOICES = (
        (RELEASE, "Apply to this release only"),
        (PRODUCT, "Apply to all product releases"),
        (CATEGORY, "Apply to all category product"),
        ("", "All products"),
    )
    SCOPE_CHOICES = ((USAGE, "This usage scope"), (ANY, "Any scope"))
    EXPLOITATION_CHOICES = ((ANY, "Apply to any exploitation"),)

    product_release = forms.ChoiceField(
        label="Products or releases",
        choices=PRODUCT_RELEASE_CHOICES,
        help_text="Rule will only apply to selected products",
    )
    scope_choice = forms.ChoiceField(
        label="Rule will only apply to selected scope", choices=SCOPE_CHOICES
    )
    exploitation_choice = forms.ChoiceField(choices=EXPLOITATION_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change labels of fields depending on product and component  names
        if self.usage.release:
            self.fields["product_release"].choices = (
                (self.RELEASE, f"Only {self.usage.release}"),
                (self.PRODUCT, f"All {self.usage.release.product} releases"),
                *(
                    (
                        category.id,
                        f'All product in "{category.name}" category',
                    )
                    for category in self.usage.release.product.categories.all()
                ),
                (self.ANY, "All products"),
            )
        if self.usage.scope:
            self.fields["scope_choice"].choices = (
                (self.USAGE, f'Only "{self.usage.scope}" scope'),
                (self.ANY, "Any scope"),
            )
        if self.usage.exploitation:
            self.fields["exploitation_choice"].choices = (
                (self.USAGE, f"Only {self.usage.get_exploitation_display()}"),
                (self.ANY, "Any exploitation"),
            )

    def save(self, **kwargs):
        if self.cleaned_data["product_release"] == self.PRODUCT:
            self.instance.product = self.usage.release.product
        elif self.cleaned_data["product_release"] == self.RELEASE:
            self.instance.release = self.usage.release
        elif self.cleaned_data["product_release"] != self.ANY:
            self.instance.category = Category.objects.get(
                pk=self.cleaned_data["product_release"]
            )
        if self.cleaned_data["exploitation_choice"] == self.USAGE:
            self.instance.exploitation = self.usage.exploitation
        if self.cleaned_data["scope_choice"] == self.USAGE:
            self.instance.scope = self.usage.scope

        return super().save(**kwargs)


class CreateLicenseChoiceForm(BaseUsageConditionForm):
    expression_out = forms.CharField(
        label="Final SPDX expression",
        help_text="The final expression of the license chosen for this usage. Can still contains ANDs, and even ORs if"
        " you want to comply with all licenses and let the end user choose.",
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
            "exploitation_choice",
            "scope_choice",
            "explanation",
        )


class CreateDerogationForm(BaseUsageConditionForm):
    LINKING_CHOICES = ((BaseUsageConditionForm.ANY, "Apply to any linking"),)
    MODIFICATION_CHOICES = (
        (BaseUsageConditionForm.ANY, "Apply to any component modification"),
    )
    linking_choice = forms.ChoiceField(choices=LINKING_CHOICES)
    modification_choice = forms.ChoiceField(choices=MODIFICATION_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change labels of fields depending on usage linking
        if self.usage.linking:
            self.fields["linking_choice"].choices = (
                (self.USAGE, f"Only {self.usage.get_linking_display()}"),
                (self.ANY, "Any linking"),
            )
        if self.usage.component_modified:
            self.fields["modification_choice"].choices = (
                (self.USAGE, f"Only {self.usage.get_component_modified_display()}"),
                (self.ANY, "Any modification"),
            )

    def save(self, **kwargs):
        if self.cleaned_data["linking_choice"] == self.USAGE:
            self.instance.linking = self.usage.linking
        if self.cleaned_data["modification_choice"] == self.USAGE:
            self.instance.modification = self.usage.component_modified

        return super().save(**kwargs)

    class Meta:
        model = Derogation
        fields = (
            "product_release",
            "scope_choice",
            "component_version",
            "linking_choice",
            "modification_choice",
            "exploitation_choice",
            "justification",
        )
