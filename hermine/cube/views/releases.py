# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic

import cube.views.licenses
from cube.models import (
    Release,
    Usage,
    Generic,
    Derogation,
    LicenseChoice,
    License,
    Version,
)
from cube.utils.licenses import (
    check_licenses_against_policy,
    get_licenses_to_check_or_create,
    explode_SPDX_to_units,
    get_usages_obligations,
)


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
        # ==== Step 2 bis ===
        response = confirm_ands(self.object.id)
        context["to_confirm"] = response["to_confirm"]
        context["confirmed"] = response["confirmed"]
        context["corrected"] = response["corrected"]

        if len(response["to_confirm"]) == 0 and validation_step == 3:
            validation_step = 4

        # ==== For step 3 ====
        response = propagate_choices(self.object.id)
        context["to_resolve"] = response["to_resolve"]
        context["resolved"] = response["resolved"]

        if len(response["to_resolve"]) == 0 and validation_step == 4:
            validation_step = 5

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

        if step_4_valid and validation_step == 5:
            validation_step = 6

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
        usages = self.object.usage_set.all()
        generics_involved, orphaned_licenses = get_usages_obligations(usages)
        context["generics_involved"] = generics_involved
        context["orphaned_licenses"] = orphaned_licenses

        return context


@login_required
def release_generic(request, release_id, generic_id):
    usages = Usage.objects.filter(
        release__id=release_id, licenses_chosen__obligation__generic__id=generic_id
    )
    generic = Generic.objects.get(pk=generic_id)
    release = Release.objects.get(pk=release_id)
    context = {"usages": usages, "generic": generic, "release": release}
    return render(request, "cube/release_generic.html", context)


@login_required
def release_exploitation(request, release_id):
    """Takes the user to the page that allows them to add an exploitation choice for
    each of the scopes in the release they're working on.

    :param request: mandatory
    :type request: HttpRequest
    :param release_id: The id of this release
    :type release_id: django AutoField
    :return: Renders the context into the template.
    :rtype: HttpResponse
    """
    release = Release.objects.get(pk=release_id)
    usage_set = release.usage_set.all()
    scope_dict = dict()
    for usage in usage_set:
        scope_dict[usage.scope] = usage.exploitation
    context = {
        "release": release,
        "scope_dict": scope_dict,
        "EXPLOITATION_CHOICES": Usage.EXPLOITATION_CHOICES,
    }
    return render(request, "cube/release_exploitation.html", context)


@login_required
def release_send_exploitation(request, release_id):
    """Digests inputs from the associated form and send it to the database.

    :param request: mandatory
    :type request: HttpRequest
    :param release_id: The id of this release
    :type release_id: django AutoField
    :return: A redirection to this release main page.
    :rtype: HttpResponseRedirect
    """
    release = get_object_or_404(Release, pk=release_id)
    usage_set = release.usage_set.all()
    scope_set = set(u.scope for u in usage_set)
    usages = [u for u in usage_set if u.scope in scope_set]
    for usage in usages:
        usage.exploitation = request.POST[usage.scope]
        usage.save()
    response = redirect("cube:release_exploitation", release_id=release_id)
    return response


@login_required
def release_add_derogation(request, release_id, usage_id):
    """Takes the user to the page that allows them to add a derogation for the release
    they're working on.

    :param request: mandatory
    :type request: HttpRequest
    :param release_id: The id of this release
    :type release_id: django AutoField
    :param usage_id: The id of this usage
    :type usage_id: django AutoField
    :return: Renders the context into the template.
    :rtype: HttpResponse
    """
    usage = Usage.objects.get(pk=usage_id)
    release = Release.objects.get(pk=release_id)
    context = {"usage": usage, "release": release}
    return render(request, "cube/release_derogation.html", context)


@login_required
def release_send_derogation(request, release_id, usage_id):
    """Digests inputs from the associated form and send it to the database.

    :param request: mandatory
    :type request: HttpRequest
    :param release_id: The id of this release
    :type release_id: django AutoField
    :param usage_id: The id of this usage
    :type usage_id: django AutoField
    :return: A redirection to this release main page.
    :rtype: HttpResponseRedirect
    """
    actionvalue = request.POST["action"]
    justificationvalue = request.POST["justification"]
    usage_derog = linking = scope = None
    usage = get_object_or_404(Usage, pk=usage_id)
    release = get_object_or_404(Release, pk=release_id)
    for license in usage.licenses_chosen.all():
        if actionvalue == "component":
            usage_derog = usage
        if actionvalue == "linking":
            linking = usage.linking
        if actionvalue == "scope":
            scope = usage.scope
        if actionvalue == "linkingscope":
            scope = usage.scope
            linking = usage.linking

        derogation = Derogation(
            release=release,
            usage=usage_derog,
            license=license,
            scope=scope,
            justification=justificationvalue,
            linking=linking,
        )
        derogation.save()

    response = redirect("cube:release_synthesis", release_id)
    return response


@login_required
def release_add_choice(request, release_id, usage_id):
    """Takes the user to the page that allows them to add a choice for a usage that has
    a complex license expression.

    :param request: mandatory
    :type request: HttpRequest
    :param release_id: The id of this release
    :type release_id: django AutoField
    :param usage_id: The id of this usage
    :type usage_id: django AutoField
    :return: Renders the context into the template.
    :rtype: HttpResponse
    """
    # TODO May be simplify the URL used: The release_id is not used to
    # ensure consistency with the release deduced from the usage
    usage = Usage.objects.get(pk=usage_id)

    if usage.version.corrected_license:
        effective_license = usage.version.corrected_license
    elif usage.version.spdx_valid_license_expr:
        effective_license = usage.version.spdx_valid_license_expr
    else:
        raise ("Choice cannot be done because no expression to process")
    choices = LicenseChoice.objects.filter(
        Q(expression_in=effective_license),
        Q(component=usage.version.component) | Q(component=None),
        Q(version=usage.version) | Q(version=None),
        Q(product=usage.release.product) | Q(product=None),
        Q(release=usage.release) | Q(release=None),
        Q(scope=usage.scope) | Q(scope=None),
    )

    context = {"usage": usage, "expression_in": effective_license, "choices": choices}
    return render(request, "cube/release_choice.html", context)


@login_required
def release_send_choice(request, release_id, usage_id):
    """Digests inputs from the associated form and send it to the database.

    :param request: mandatory
    :type request: HttpRequest
    :param release_id: The id of this release
    :type release_id: django AutoField
    :param usage_id: The id of this usage
    :type usage_id: django AutoField
    :return: A redirection to this release main page.
    :rtype: HttpResponseRedirect
    """

    expression_in = None
    usage = get_object_or_404(Usage, pk=usage_id)
    expression_out = request.POST["expression_out"]
    range_scope = request.POST["range_scope"]
    range_component = request.POST["range_component"]
    range_product = request.POST["range_product"]
    explanation = request.POST["explanation"]

    # First we apply the choice to the usage
    if usage.version.corrected_license:
        expression_in = usage.version.corrected_license
    else:
        expression_in = usage.version.spdx_valid_license_expr
    usage.license_expression = expression_out
    lic_to_add = set()
    for uniq_lic_id in set(explode_SPDX_to_units(expression_out)):
        unique_license = License.objects.get(spdx_id__exact=uniq_lic_id)
        lic_to_add.add(unique_license)
    usage.licenses_chosen.set(lic_to_add)
    usage.save()

    # Then we store this choice
    if range_scope == "any":
        scope = None
    else:
        scope = usage.scope

    component = usage.version.component
    version = usage.version
    if range_component == "any":
        component = None
        version = None
    elif range_component == "component":
        version = None

    product = usage.release.product
    release = usage.release
    if range_product == "any":
        product = None
        release = None
    elif range_component == "product":
        release = None

    choice, created = LicenseChoice.objects.update_or_create(
        expression_in=expression_in,
        product=product,
        release=release,
        component=component,
        version=version,
        scope=scope,
        defaults={"expression_out": expression_out, "explanation": explanation},
    )

    response = redirect("cube:release_synthesis", release_id)
    return response


def propagate_choices(release_id):
    """
    Transfer license information from component to usage. Set usage.license_chosen if
    there is no ambiguity.

    Args:

        release_id (int): The intern identifier of the concerned release

    Returns:
        response: A python object that has two field :
            `to_resolve` the set of usages which needs an explicit choice
            `resolved` the set of usages for which a choice has just been made
    """

    release = Release.objects.get(pk=release_id)

    to_resolve = set()
    resolved = set()

    unchosen_usages = release.usage_set.all().filter(license_expression="")
    for usage in unchosen_usages:
        if usage.version.corrected_license:
            effective_license = usage.version.corrected_license
        else:
            effective_license = usage.version.spdx_valid_license_expr
        unique_lic_ids = explode_SPDX_to_units(effective_license)
        if len(unique_lic_ids) == 1:
            try:
                unique_license = License.objects.get(spdx_id__exact=unique_lic_ids[0])
                usage.licenses_chosen.set(set([unique_license]))
                usage.license_expression = unique_lic_ids[0]
                usage.save()
            except License.DoesNotExist:
                print("Can't choose an unknown license", unique_lic_ids[0])
        else:
            choices = LicenseChoice.objects.filter(
                Q(expression_in=effective_license),
                Q(component=usage.version.component) | Q(component=None),
                Q(version=usage.version) | Q(version=None),
                Q(product=usage.release.product) | Q(product=None),
                Q(release=usage.release) | Q(release=None),
                Q(scope=usage.scope) | Q(scope=None),
            )
            expression_outs = []
            for choice in choices:
                expression_outs.append(choice.expression_out)
            if len(set(expression_outs)) == 1:
                usage.license_expression = expression_outs[0]
                lic_to_add = set()
                for uniq_lic_id in set(explode_SPDX_to_units(expression_outs[0])):
                    unique_license = License.objects.get(spdx_id__exact=uniq_lic_id)
                    lic_to_add.add(unique_license)

                usage.licenses_chosen.set(lic_to_add)
                usage.save()
                resolved.add(usage)
            else:
                to_resolve.add(usage)

    response = {"to_resolve": to_resolve, "resolved": resolved}
    return response


def confirm_ands(release_id):
    """
    Because of unreliable metadata, many "Licence1 AND Licence2" expressions
    actually meant to be "Licence1 AND Licence2". That's why any expression of
    this type has to be manually validated.

    Args:

        release_id (int): The intern identifier of the concerned release

    Returns:
        response: A python object that has three fields :
            `to_confirm` the set of versions that needs an explicit confirmation
            `confirmed` the set of version whose AND has been confirmed
            `corrected` the set of version whose AND has been corrected
    """

    release = Release.objects.get(pk=release_id)

    to_confirm = set()
    confirmed = set()
    corrected = set()

    # TODO we should take into account cases like "(MIT OR ISC)AND Apache-3.0)"
    # with no space before the "AND"
    to_confirm = (
        Version.objects.filter(usage__release_id=release_id)
        .filter(spdx_valid_license_expr__contains=" AND ")
        .filter(Q(corrected_license="") | Q(corrected_license=None))
    )
    confirmed = (
        Version.objects.filter(usage__release_id=release_id)
        .filter(spdx_valid_license_expr__contains=" AND ")
        .filter(Q(corrected_license=F("spdx_valid_license_expr")))
    )
    corrected = (
        Version.objects.filter(usage__release_id=release_id)
        .filter(spdx_valid_license_expr__contains=" AND ")
        .exclude(
            Q(corrected_license=F("spdx_valid_license_expr"))
            | Q(corrected_license="")
            | Q(corrected_license=None)
        )
    )
    response = {
        "to_confirm": to_confirm,
        "confirmed": confirmed,
        "corrected": corrected,
    }
    return response
