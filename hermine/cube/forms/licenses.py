#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from django.db import transaction
from django.forms import ModelForm, ModelChoiceField, Form

from cube.models import Generic, Obligation, License


class ObligationGenericDiffForm(ModelForm):
    generic = ModelChoiceField(queryset=Generic.objects.all(), to_field_name="name")

    class Meta:
        model = Obligation
        fields = ("generic",)


class CopyReferenceLicensesForm(Form):
    """Form to copy all missing licenses to local data from reference."""

    @transaction.atomic()
    def save(self):
        """Copy all missing licenses to local data from reference."""
        missing_licenses = License.objects.using("shared").exclude(
            spdx_id__in=list(License.objects.all().values_list("spdx_id", flat=True))
        )

        missing_generics = (
            Generic.objects.using("shared")
            .filter(
                obligation__in=Obligation.objects.using("shared").filter(
                    license__in=missing_licenses
                )
            )
            .exclude(
                name__in=list(Generic.objects.all().values_list("name", flat=True))
            )
            .distinct()
        )

        # Copy missing generics
        for generic in missing_generics:
            generic.id = None
            generic.save(using="default")

        # Copy licenses then their obligations
        for lic in missing_licenses:
            obligations = list(lic.obligation_set.all())
            lic.id = None
            lic.save(using="default")
            for obligation in obligations:
                if obligation.generic is not None:
                    generic_name = obligation.generic.name
                obligation.id = None
                obligation._state.db = "default"
                obligation.license = lic
                if obligation.generic is not None:
                    obligation.generic = Generic.objects.get(name=generic_name)
                obligation.save(using="default")


class CopyReferenceGenericsForm(Form):
    """Form to copy all missing generic obligations to local data from reference."""

    def save(self):
        """Copy all missing licenses to local data from reference."""
        missing_generics = Generic.objects.using("shared").exclude(
            name__in=list(Generic.objects.all().values_list("name", flat=True))
        )

        # Copy missing generics
        for generic in missing_generics:
            generic.id = None
            generic.save(using="default")


class CopyReferenceObligationForm(Form):
    obligation = ModelChoiceField(queryset=Obligation.objects.using("shared").all())

    def save(self):
        obligation = self.cleaned_data["obligation"]
        spdx_id = obligation.license.spdx_id
        if obligation.generic is not None:
            generic_name = obligation.generic.name
        obligation.id = None
        obligation._state.db = "default"
        obligation.license = License.objects.get(spdx_id=spdx_id)
        if obligation.generic is not None:
            obligation.generic = Generic.objects.get(name=generic_name)
        obligation.save(using="default")
        return obligation
