# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
import json
from json import JSONDecodeError

from django import forms
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Release, Usage, LicenseChoice
from .models.policy import LicenseCuration, Derogation
from .utils.generics import handle_generics_json
from .utils.licenses import handle_licenses_json


class BaseJsonImportForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data["file"].read()

        try:
            json.loads(file)
        except JSONDecodeError:
            raise ValidationError("The file is not a valid JSON file")

        return file


class ImportGenericsForm(BaseJsonImportForm):
    def save(self):
        file = self.cleaned_data["file"]
        try:
            handle_generics_json(file)
        except serializers.ValidationError as e:
            raise ValidationError(str(e))
        except KeyError:
            raise ValidationError('Each generic object must have a "id" field.')


class ImportLicensesForm(BaseJsonImportForm):
    def save(self):
        file = self.cleaned_data["file"]
        try:
            handle_licenses_json(file)
        except serializers.ValidationError as e:
            raise ValidationError(e.message)
        except KeyError:
            raise ValidationError('Each license object must have a "spdx_id" field.')


class ImportBomForm(forms.ModelForm):
    BOM_ORT = "ORTBom"
    BOM_SPDX = "SPDXBom"
    BOM_CHOICES = (
        (BOM_ORT, "ORT Evaluated model"),
        (BOM_SPDX, "SPDX Bill of Materials"),
    )
    IMPORT_MODE_MERGE = "Merge"
    IMPORT_MODE_REPLACE = "Replace"
    IMPORT_MODE_CHOICES = (
        (
            IMPORT_MODE_REPLACE,
            "Delete all previously saved component usages and remplace with new import",
        ),
        (IMPORT_MODE_MERGE, "Add new component usages while keeping previous ones"),
    )
    bom_type = forms.ChoiceField(label="File format", choices=BOM_CHOICES)
    file = forms.FileField()
    import_mode = forms.ChoiceField(
        choices=IMPORT_MODE_CHOICES, widget=forms.RadioSelect
    )
    linking = forms.ChoiceField(
        choices=((None, "---"), *Usage.LINKING_CHOICES),
        required=False,
        initial=None,
        label="Components linking",
    )

    class Meta:
        model = Release
        fields = "bom_type", "file"


class BaseComponentDecisionForm(forms.ModelForm):
    ANY = "any"
    COMPONENT = "component"
    VERSION = "version"
    COMPONENT_VERSION_CHOICES = (
        (VERSION, "Apply to this version only"),
        (COMPONENT, "Apply to all component versions"),
        ("", "All components"),
    )

    component_version = forms.ChoiceField(choices=COMPONENT_VERSION_CHOICES)

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

    product_release = forms.ChoiceField(choices=PRODUCT_RELEASE_CHOICES)
    scope_choice = forms.ChoiceField(choices=SCOPE_CHOICES)

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


class BaseCreateUsageDecisionChoiceForm(BaseUsageConditionForm):
    class Meta:
        fields = (
            "expression_out",
            "product_release",
            "component_version",
            "scope_choice",
            "explanation",
        )


class CreateLicenseCurationForm(BaseComponentDecisionForm):
    def save(self, **kwargs):
        self.instance.expression_in = self.usage.version.declared_license_expr
        return super().save(**kwargs)

    class Meta(BaseComponentDecisionForm.Meta):
        model = LicenseCuration


class CreateLicenseChoiceForm(BaseCreateUsageDecisionChoiceForm):
    class Meta(BaseCreateUsageDecisionChoiceForm.Meta):
        model = LicenseChoice


class DerogationForm(BaseUsageConditionForm):
    USAGE_LINKING = "usage"
    LINKING_CHOICES = ((BaseUsageConditionForm.ANY, "Apply to any linking"),)

    linking_choice = forms.ChoiceField(choices=LINKING_CHOICES)

    def __init__(self, *args, **kwargs):
        self.license = kwargs.pop("license")
        super().__init__(*args, **kwargs)
        # Change labels of fields depending on usage linking
        if self.usage.linking:
            self.fields["linking_choice"].choices = (
                (self.USAGE_LINKING, f"Only {self.usage.get_linking_display()}"),
                (self.ANY, "Any linking"),
            )

    def save(self, **kwargs):
        self.instance.license = self.license

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
