#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

#
import json
from json import JSONDecodeError

from django import forms
from django.core.exceptions import ValidationError
from django.core.serializers.base import DeserializationError

from cube.models import Release, Usage, SBOMImport
from cube.utils.generics import handle_generics_json
from cube.utils.licenses import handle_licenses_json_or_shared_json
from cube.utils.validators import validate_file_size


class BaseJsonImportForm(forms.Form):
    file = forms.FileField(validators=[validate_file_size])

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
            handle_licenses_json_or_shared_json(file)
        except DeserializationError as e:
            raise ValidationError(
                str(e) or "An error occurred while importing licenses."
            )
        except KeyError:
            raise ValidationError('Each license object must have a "spdx_id" field.')


class ImportBomForm(forms.ModelForm):
    bom_type = forms.ChoiceField(label="File format", choices=SBOMImport.BOM_CHOICES)
    file = forms.FileField(validators=[validate_file_size])
    import_mode = forms.ChoiceField(
        choices=SBOMImport.IMPORT_MODE_CHOICES, widget=forms.RadioSelect
    )
    component_update_mode = forms.ChoiceField(
        choices=SBOMImport.COMPONENT_UPDATE_CHOICES,
        help_text="When a component is already present in Hermine database, "
        "you can choose to override all its informations with this SBOM content. "
        "Be aware that this may impact other products or release validations on the instance.",
    )
    linking = forms.ChoiceField(
        choices=((None, "---"), *Usage.LINKING_CHOICES),
        required=False,
        initial=None,
        label="Components linking",
    )
    default_project_name = forms.CharField(
        max_length=Usage.MAX_LENGTH_DEFAULT_PROJECT_NAME, required=False
    )
    default_scope_name = forms.CharField(
        max_length=Usage.MAX_LENGTH_DEFAULT_SCOPE_NAME, required=False
    )

    class Meta:
        model = Release
        fields = "bom_type", "file"
