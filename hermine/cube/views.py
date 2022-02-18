# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
    Product,
    Release,
    Component,
)
from .f_views import (
    propagate_choices,
    check_licenses_against_policy,
    get_licenses_to_check_or_create,
)


class ProductListView(LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = "cube/product_list.html"
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nb_products"] = Product.objects.all().count()
        context["nb_releases"] = Release.objects.all().count()
        return context


class ReleaseView(LoginRequiredMixin, generic.DetailView):
    """
    Shows 4 validation steps for a release of a product:
    step 1 : checks that licence metadata are present and correct
    step 2 : checks that all licences have been reviewed by legal dpt
    step 3 : resolves choices in case of multi-licences
    step 4 : checks that chosen licences are compatible with policy and derogs
    """

    model = Release
    template_name = "cube/release.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        validation_step = 1

        # ==== Step 1 ====
        # Looking for licenses that haven't been normalized, that is to say the ones
        # that do not have a name fitting SPDX standards or that do not have been
        # manually corrected.
        unnormalized_usages = self.object.usage_set.all().filter(
            version__spdx_valid_license_expr="", version__corrected_license=""
        )
        nb_validated_components = len(self.object.usage_set.all()) - len(
            unnormalized_usages
        )
        if len(unnormalized_usages) == 0:
            validation_step = 2

        context["unnormalized_usages"] = unnormalized_usages
        context["nb_validated_components"] = nb_validated_components

        # ==== Step 2 ===
        licenses = get_licenses_to_check_or_create(self.object)

        context["licenses_to_check"] = licenses["licenses_to_check"]
        context["licenses_to_create"] = licenses["licenses_to_create"]
        if (
            len(context["licenses_to_check"]) == 0
            and len(context["licenses_to_create"]) == 0
            and validation_step == 2
        ):
            validation_step = 3

        # ==== For step 3 ====
        response = propagate_choices(self.object.id)
        context["to_resolve"] = response["to_resolve"]
        context["resolved"] = response["resolved"]

        if len(response["to_resolve"]) == 0 and validation_step == 3:
            validation_step = 4

        # ==== For step 4 ====
        r = check_licenses_against_policy(self.object)

        if len(r["usages_lic_grey"]) > 0 and validation_step > 2:
            validation_step = 2

        if (
            len(r["usages_lic_red"]) == 0
            and len(r["usages_lic_orange"]) == 0
            and len(r["usages_lic_grey"]) == 0
        ):
            step_4_valid = True
        else:
            step_4_valid = False

        if step_4_valid and validation_step == 4:
            validation_step = 5

        context["usages_lic_red"] = r["usages_lic_red"]
        context["usages_lic_orange"] = r["usages_lic_orange"]
        context["usages_lic_grey"] = r["usages_lic_grey"]
        context["step_4_valid"] = step_4_valid
        context["involved_lic"] = r["involved_lic"]
        context["derogations"] = r["derogations"]

        self.object.valid_step = validation_step
        self.object.save()
        return context


class ReleaseBomView(LoginRequiredMixin, generic.DetailView):
    model = Release
    template_name = "cube/release_bom.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ReleaseObligView(LoginRequiredMixin, generic.DetailView):
    """
    Lists relevant obligations for a given release
    """

    model = Release
    template_name = "cube/release_oblig.html"

    def matchObligationExploitation(self, expl, explTrigger):
        """
        A small utility to check the pertinence of an Obligation in the exploitation
        context of a usage.

        :param expl: The type of exploitation of the component
        :type expl: A string in ["Distribution", "DistributionSource",
            "DistributionNonSource", "NetworkA "Network access"),ccess", "InternalUse"
        :param explTrigger: The type of exploitation that triggers the obligation
        :type explTrigger: A string in ["Distribution", "DistributionSource",
            "DistributionNonSource", "NetworkA "Network access"),ccess", "InternalUse"
        :return: True if the exploitation meets the exploitation trigger
        :rtype: Boolean
        """
        if explTrigger in expl:
            return True
        elif (
            explTrigger == "DistributionSource"
            or explTrigger == "DistributionNonSource"
        ) and expl == "Distribution":
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        generics_involved = set()
        orphaned_licenses = set()

        for usage in self.object.usage_set.all():
            for license in usage.licenses_chosen.all():
                # Those two lines allow filtering obligations depending on the Usage
                # context (if the component has been modified and how it's being
                # distributed)
                obligations_filtered = [
                    o
                    for o in license.obligation_set.all()
                    if usage.component_modified in o.trigger_mdf
                ]
                obligations_filtered = [
                    o
                    for o in obligations_filtered
                    if self.matchObligationExploitation(
                        usage.exploitation, o.trigger_expl
                    )
                ]
                for obligation in obligations_filtered:
                    if obligation.generic:
                        generics_involved.add(obligation.generic)
                    else:
                        orphaned_licenses.add(license)
        context["generics_involved"] = generics_involved
        context["orphaned_licenses"] = orphaned_licenses
        return context


class ComponentList(LoginRequiredMixin, generic.ListView):
    model = Component
    paginate_by = 50
    ordering = ["name"]


class ComponentView(LoginRequiredMixin, generic.DetailView):
    template_name = "cube/component.html"
    model = Component

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
