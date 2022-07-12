# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.forms import Form, ChoiceField, Select
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic import UpdateView

from cube.forms import ImportBomForm
from cube.importers import import_ort_evaluated_model_json_file, import_spdx_file
from cube.models import (
    Release,
    Usage,
    Generic,
    Derogation,
    LicenseChoice,
    License,
    Exploitation,
)
from cube.utils.licenses import (
    explode_spdx_to_units,
    get_usages_obligations,
)
from cube.utils.releases import update_validation_step


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

        return {
            **context,
            **update_validation_step(self.object),
        }


class ReleaseBomView(LoginRequiredMixin, UpdateView):
    model = Release
    form_class = ImportBomForm
    context_object_name = "release"
    template_name = "cube/release_bom.html"
    import_status = None

    def form_valid(self, form):
        self.import_status = "success"
        replace = form.cleaned_data["import_mode"] == ImportBomForm.IMPORT_MODE_REPLACE
        try:
            if form.cleaned_data["bom_type"] == ImportBomForm.BOM_ORT:
                import_ort_evaluated_model_json_file(
                    self.request.FILES["file"],
                    self.object.pk,
                    replace,
                    defaults={"linking": form.cleaned_data.get("linking")},
                )
            elif form.cleaned_data["bom_type"] == ImportBomForm.BOM_SPDX:
                import_spdx_file(
                    self.request.FILES["file"],
                    self.object.pk,
                    replace,
                    defaults={"linking": form.cleaned_data.get("linking")},
                )
        except:  # noqa: E722 TODO
            self.import_status = "error"

        return super().render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        kwargs["import_status"] = self.import_status
        return super().get_context_data(**kwargs)


class ReleaseObligView(LoginRequiredMixin, generic.DetailView):
    """
    Lists relevant obligations for a given release
    """

    model = Release
    template_name = "cube/release_oblig.html"

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


class ReleaseExploitationForm(Form):
    def __init__(self, instance, *args, **kwargs):
        self.release = instance
        super().__init__(*args, **kwargs)
        for scope in self.release.usage_set.values("scope").annotate(count=Count("*")):
            self.fields[scope["scope"]] = ChoiceField(
                choices=Usage.EXPLOITATION_CHOICES,
                widget=Select(attrs={"class": "select"}),
                label=f"{scope['scope']} ({scope['count']} components)",
            )

            try:
                self.initial[scope["scope"]] = self.release.exploitation_set.get(
                    scope=scope["scope"]
                ).exploitation
            except Exploitation.DoesNotExist:
                pass

    def save(self):
        for scope, exploitation_type in self.cleaned_data.items():
            Exploitation.objects.update_or_create(
                release=self.release,
                scope=scope,
                defaults={"exploitation": exploitation_type},
            )
            self.release.usage_set.filter(scope=scope).update(
                exploitation=exploitation_type
            )

        return self.release


class ReleaseExploitationView(UpdateView):
    model = Release
    context_object_name = "release"
    template_name = "cube/release_exploitation.html"
    form_class = ReleaseExploitationForm

    def get_success_url(self):
        return reverse("cube:release_exploitation", args=[self.object.pk])


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

    response = redirect("cube:release_detail", release_id)
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
        print("Choice cannot be done because no expression to process")
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
    for uniq_lic_id in set(explode_spdx_to_units(expression_out)):
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

    response = redirect("cube:release_detail", release_id)
    return response
