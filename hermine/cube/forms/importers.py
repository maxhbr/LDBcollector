#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

#
import json
from json import JSONDecodeError

from django import forms
from django.core.exceptions import ValidationError
from django.core.serializers.base import DeserializationError

from cube.models import Release, Usage
from cube.utils.generics import handle_generics_json
from cube.utils.licenses import handle_licenses_json


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
        except DeserializationError as e:
            raise ValidationError(str(e))
        except KeyError:
            raise ValidationError('Each generic object must have a "id" field.')


class ImportLicensesForm(BaseJsonImportForm):
    def save(self):
        file = self.cleaned_data["file"]
        try:
            handle_licenses_json(file)
        except DeserializationError as e:
            raise ValidationError(str(e))
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
