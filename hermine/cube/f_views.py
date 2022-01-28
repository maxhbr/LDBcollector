# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

import requests, json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count
from django.conf import settings
from django.core.serializers import serialize, deserialize
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage

from cube.serializers import (
    LicenseSerializer,
    ObligationSerializer,
    GenericSerializer,
    UsageSerializer,
    ExploitationSerializer,
    ProductSerializer,
    ReleaseSerializer,
    ComponentSerializer,
    VersionSerializer,
    UploadSPDXSerializer,
    NormalisedLicensesSerializer,
    DerogationSerializer,
)

from .models import (
    Product,
    Release,
    Usage,
    License,
    Obligation,
    Generic,
    Component,
    Derogation,
    Version,
    Team,
    LicenseChoice,
)
from django.db.models import Q
from .forms import ImportLicensesForm, ImportGenericsForm, ImportBomForm
from .importTools import (
    import_licenses_file,
    import_ort_file,
    import_yocto_file,
    import_spdx_file,
)

from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import H, P, Span

# Tool functions


def flatten(t):
    return [item for sublist in t for item in sublist]


def explode_SPDX_to_units(SPDX_expr):
    """Extract a list of every license from a SPDX valid expression.

        :param SPDX_expr: A string that represents a valid SPDX expression. (Like ")
        :type SPDX_expr: string
        :return: A list of valid SPDX licenses contained in the expression.
        :rtype: list
        """
    licenses = []
    raw_expression = SPDX_expr.replace("(", "").replace(")", "")
    # Next line allows us to consider an SPDX expression that has a 'WITH' clause as a full SPDX expression
    raw_expression = raw_expression.replace(" WITH ", "_WITH_")
    chunks = raw_expression.split()
    while "AND" in chunks:
        chunks.remove("AND")
    while "OR" in chunks:
        chunks.remove("OR")
    i = 0
    while i < len(chunks):
        if chunks[i] not in licenses:
            chunks[i] = chunks[i].replace("_WITH_", " WITH ")
            licenses.append(chunks[i])
        i += 1
    return licenses


def get_licenses_to_check_or_create(release):
    response = {}
    validated_usages = release.usage_set.all().filter(
        version__spdx_valid_license_expr__isnull=False
    )
    corrected_usages = release.usage_set.all().filter(
        version__corrected_license__isnull=False
    )
    validated_usages |= corrected_usages
    licenses_to_check = set()
    licenses_to_create = set()
    for usage in validated_usages:
        if usage.version.corrected_license:
            raw_expression = usage.version.corrected_license
        else:
            raw_expression = usage.version.spdx_valid_license_expr
        SPDX_Licenses = explode_SPDX_to_units(raw_expression)

        for license in SPDX_Licenses:
            try:
                l = License.objects.get(spdx_id=license)
                if l.color == "Grey":
                    licenses_to_check.add(l)
            except License.DoesNotExist:
                # It might happen that SPDX throws 'NOASSERTION' instead of an empty string. Handling that.
                if license != "NOASSERTION":
                    licenses_to_create.add(license)
                    print("unknown license", license)

    response["licenses_to_check"] = licenses_to_check
    response["licenses_to_create"] = licenses_to_create
    return response


# Class based functions


@login_required
def index(request):

    latest_license_list = License.objects.filter(status="Tocheck").annotate(
        Count("obligation")
    )
    nb_products = Product.objects.all().count()
    nb_releases = Release.objects.all().count()
    nb_components = Component.objects.all().count()
    nb_licenses = License.objects.all().count()

    context = {
        "latest_license_list": latest_license_list,
        "nb_products": nb_products,
        "nb_releases": nb_releases,
        "nb_components": nb_components,
        "nb_licenses": nb_licenses,
    }
    return render(request, "cube/index.html", context)


@login_required
def licenses(request, page=1):
    form = ImportLicensesForm(request.POST, request.FILES)
    licenses = License.objects.all()
    paginator = Paginator(licenses, 50)

    try:
        licenses = paginator.page(page)
    except EmptyPage:
        licenses = paginator.page(paginator.num_pages)

    context = {"licenses": licenses, "form": form}
    return render(request, "cube/license_list.html", context)


@login_required
def license(request, license_id):
    context = {}
    license = get_object_or_404(License, pk=license_id)
    orphan_obligations = license.obligation_set.filter(generic__isnull=True)
    generic_obligations = license.obligation_set.filter(
        generic__in_core=False
    ).order_by("generic__id")
    core_obligations = license.obligation_set.filter(generic__in_core=True).order_by(
        "generic__id"
    )
    form = ImportLicensesForm
    if license.inspiration:
        context.update({"inspiration": license.inspiration})
    elif license.inspiration_spdx:
        try:
            inspiration = License.objects.get(spdx_id=license.inspiration_spdx)
            context.update({"inspiration": inspiration})
        except Exception:
            print(
                "Unable to find the inspiration in database", license.inspiration_spdx
            )
    context.update(
        {
            "license": license,
            "orphan_obligations": orphan_obligations,
            "obligations_in_generic": generic_obligations,
            "obligations_in_core": core_obligations,
            "form": form,
        }
    )
    return render(request, "cube/license.html", context)


@login_required
def generics(request):
    form = ImportGenericsForm(request.POST, request.FILES)
    generics_incore = Generic.objects.filter(in_core=True)
    generics_outcore = Generic.objects.filter(in_core=False)
    context = {
        "generics_incore": generics_incore,
        "generics_outcore": generics_outcore,
        "form": form,
    }
    return render(request, "cube/generic_list.html", context)


@login_required
def generic(request, generic_id):
    generic = get_object_or_404(Generic, pk=generic_id)
    context = {"generic": generic}
    return render(request, "cube/generic.html", context)


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


def import_bom(request):
    form = ImportBomForm(request.POST, request.FILES)
    status = None
    if form.is_valid():
        status = "success"
        try:
            if form.cleaned_data["bom_type"] == "ORTBom":
                import_ort_file(request.FILES["file"], form.cleaned_data["release"].id)

            elif form.cleaned_data["bom_type"] == "SPDXBom":
                import_spdx_file(request.FILES["file"], form.cleaned_data["release"].id)

        except:
            print("The file you chose do not match the format you chose.")
            status = "error"

        return render(
            request,
            "cube/import_bom.html",
            {
                "form": form,
                "status": status,
                "release_id": form.cleaned_data["release"].id,
            },
        )
    else:
        form = ImportBomForm()
        return render(request, "cube/import_bom.html", {"form": form, "status": status})


def handle_generics_file(request):
    genericsFile = request.FILES["file"]
    csrftoken = request.COOKIES["csrftoken"]
    genericsArray = json.load(genericsFile)
    for generic in genericsArray:
        try:
            g = Generic.objects.get(pk=generic["pk"])
        except Generic.DoesNotExist:
            print("instantiation of a new Generic object with pk = ", generic["pk"])
            g = Generic(generic["pk"])
        s = GenericSerializer(g, data=generic["fields"], partial=True)
        s.is_valid(raise_exception=True)
        s.save()


def upload_generics_file(request):
    if request.method == "POST":
        handle_generics_file(request)
        return redirect("cube:generics")

    return render(request, "cube/generic_list.html")


def handle_licenses_file(request):
    licenseFile = request.FILES["file"]
    licenseArray = json.load(licenseFile)
    # Handling case of a JSON that only contains one license and is not a list (single license purpose)
    if type(licenseArray) is dict:
        try:
            l = License.objects.get(spdx_id=licenseArray["spdx_id"])
        except License.DoesNotExist:
            print("Instantiation of a new License object with pk = ", licenseArray)
            l = License()
            l.save()
        s = LicenseSerializer(l, data=licenseArray)
        s.is_valid(raise_exception=True)
        print(s.errors)
        s.save()
    # Handling case of a JSON that contains multiple licenses and is a list (multiple licenses purpose)
    elif type(licenseArray) is list:
        for license in licenseArray:
            try:
                l = License.objects.get(spdx_id=license["spdx_id"])
            except License.DoesNotExist:
                print("Instantiation of a new License object with pk = ", license)
                l = License()
                l.save()
            s = LicenseSerializer(l, data=license)
            s.is_valid(raise_exception=True)
            print(s.errors)
            s.save()
    else:
        print("Type of JSON neither is a list nor a dict")


@csrf_exempt
def upload_licenses_file(request):
    if request.method == "POST":
        form = ImportLicensesForm(request.POST, request.FILES)
        if form.is_valid():
            handle_licenses_file(request)
            return redirect(request.META["HTTP_REFERER"])
        else:
            form = ImportLicensesForm()
    return redirect(request.META["HTTP_REFERER"])


# def export_licenses(request):
#     """An export function that uses the License Serializer on all the licenses.
#     Effective, but using the the other one which calls the API might allow to handle specific cases such as access restrictions
#     """
#     filename = "licenses.json"
#     serializer = LicenseSerializer
#     data = serializer(License.objects.all(), many=True).data
#     with open(filename, "w+"):
#         response = HttpResponse(json.dumps(data, indent=4), content_type="application/json")
#         response["Content-Disposition"] = "attachment; filename=%s" % filename
#         return response
def export_licenses(request):
    """Calls API to retrieve list of licenses. Handles DRF pagination.

        :return: HttpResponse that triggers the download of a JSON file containing every license in a JSON Array.
        :rtype: DjangoHttpResponse
        """
    request_uri = settings.API_BASE_URL + "licenses/?format=json"
    filename = "licenses.json"
    with open(filename, "w+"):
        r = requests.get(request_uri)
        json_r = r.json()
        licenseJSONArray = json_r["results"]
        while json_r["next"]:
            r = requests.get(json_r["next"])
            json_r = r.json()
            for license in json_r["results"]:
                licenseJSONArray.append(license)
        response = HttpResponse(
            json.dumps(licenseJSONArray, indent=4), content_type="application/json"
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


def export_specific_license(request, license_id):
    l = License.objects.get(id=license_id)
    filename = l.spdx_id + ".json"
    serializer = LicenseSerializer
    data = serializer(l).data
    with open(filename, "w+"):
        response = HttpResponse(
            json.dumps(data, indent=4), content_type="application/json"
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


def export_generics(request):
    filename = "generics.json"
    with open(filename, "w+"):
        response = HttpResponse(
            serialize("json", Generic.objects.all(), cls=DjangoJSONEncoder),
            content_type="application/json",
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


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
    """Takes the user to the page that allows them to add an exploitation choice for each of the scopes in the release they're working on.

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
    """Takes the user to the page that allows them to add a derogation for the release they're working on.

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
    """Takes the user to the page that allows them to add a choice for a usage that has a complex license expression.

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
    Transfer license information from component to usage. Set usage.license_chosen if there is no ambiguity.

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


def about(request):
    context = {}
    return render(request, "cube/about.html", context)


def check_licenses_against_policy(release):
    response = {}
    usages_lic_red = set()
    usages_lic_orange = set()
    usages_lic_grey = set()
    involved_lic = set()

    derogations = release.derogation_set.all()
    usages = release.usage_set.all()

    release_derogs = dict()
    for derog in derogations:
        if derog.license.id not in release_derogs:
            release_derogs[derog.license.id] = dict()
            release_derogs[derog.license.id]["usages"] = set()
            release_derogs[derog.license.id]["scopes"] = set()
        if derog.usage:
            release_derogs[derog.license.id]["usages"].add(derog.usage)
        if derog.scope:
            release_derogs[derog.license.id]["scopes"].add(derog.scope)

    for usage in usages:
        for license in usage.licenses_chosen.all():
            involved_lic.add(license)
            derogate = (license.id in release_derogs) and (
                (
                    not (release_derogs[license.id]["usages"])
                    and not (release_derogs[license.id]["scopes"])
                )
                or usage in release_derogs[license.id]["usages"]
                or usage.scope in release_derogs[license.id]["scopes"]
            )
            if license.color == "Red" and not derogate:
                usages_lic_red.add(usage)
            elif license.color == "Orange" and not derogate:
                usages_lic_orange.add(usage)
            elif license.color == "Grey" and not derogate:
                usages_lic_grey.add(usage)

    response["usages_lic_red"] = usages_lic_red
    response["usages_lic_orange"] = usages_lic_orange
    response["usages_lic_grey"] = usages_lic_grey
    response["involved_lic"] = involved_lic
    response["derogations"] = derogations

    return response


def print_license(request, license_id):
    l = get_object_or_404(License, pk=license_id)
    filename = l.spdx_id + ".odt"
    with open(filename, "w+"):
        response = HttpResponse(content_type="application/vnd.oasis.opendocument.text")
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        
        textdoc = OpenDocumentText()
        s = textdoc.styles

        h1style = Style(name="Heading 1", family="paragraph")
        h1style.addElement(TextProperties(attributes={'fontsize':"24pt",'fontweight':"bold"}))
        s.addElement(h1style)
        h1style.addElement(ParagraphProperties(attributes={'marginbottom': '1cm'}))
        h2style = Style(name="Heading 2", family="paragraph")
        h2style.addElement(TextProperties(attributes={'fontsize':"18pt",'fontweight':"bold" }))
        h2style.addElement(ParagraphProperties(attributes={'marginbottom': '0.6cm', 'margintop': '0.4cm'}))
        s.addElement(h2style)

        h3style = Style(name="Heading 3", family="paragraph")
        h3style.addElement(TextProperties(attributes={'fontsize':"14pt",'fontweight':"bold" }))
        h3style.addElement(ParagraphProperties(attributes={'marginbottom': '0.2cm', 'margintop': '0.4cm'}))

        s.addElement(h3style)

        itstyle = Style(name="Italic", family="paragraph")
        itstyle.addElement(TextProperties(attributes={'textemphasize':"true"}))
        itstyle.addElement(ParagraphProperties(attributes={'margintop': '3cm'}))

        s.addElement(itstyle)

        # An automatic style
        boldstyle = Style(name="Bold", family="text")
        boldprop = TextProperties(fontweight="bold")
        boldstyle.addElement(boldprop)
        textdoc.automaticstyles.addElement(boldstyle)

        textdoc.automaticstyles.addElement(itstyle)

        # Text
        h=H(outlinelevel=1, stylename=h1style, text=l.long_name)
        textdoc.text.addElement(h)
        h=H(outlinelevel=1, stylename=h2style, text=l.spdx_id)
        textdoc.text.addElement(h)

        p = P(text="Validation Color: ")
        v = Span(stylename=boldstyle, text=l.color)
        p.addElement(v)
        textdoc.text.addElement(p)

        if l.color_explanation is not None:
            p = P(text="Explanation: ")
            v = Span(stylename=boldstyle, text=l.color_explanation)
            p.addElement(v)
            textdoc.text.addElement(p)

        p = P(text="Copyleft: ")
        v = Span(stylename=boldstyle, text=l.copyleft)
        p.addElement(v)
        textdoc.text.addElement(p)

        p = P(text="Considered as Free Open Source Sofware: ")
        v = Span(stylename=boldstyle, text=l.foss)
        p.addElement(v)
        textdoc.text.addElement(p)

        p = P(text="Approved by OSI: ")
        v = Span(stylename=boldstyle, text=l.osi_approved)
        p.addElement(v)
        textdoc.text.addElement(p)

        p = P(text="Has an ethical clause: ")
        v = Span(stylename=boldstyle, text=l.ethical_clause)
        p.addElement(v)
        textdoc.text.addElement(p)

        if l.verbatim:
            p = P(text="Verbatim: ")
            value = Span(text=l.verbatim)
            p.addElement(value)
            textdoc.text.addElement(p)

        if l.comment:
            p = P(text="Comment: ")
            value = Span(stylename=boldstyle, text=l.comment)
            p.addElement(v)
            textdoc.text.addElement(p)
        
        h=H(outlinelevel=1, stylename=h2style, text="List of identified obligations")
        textdoc.text.addElement(h)

        for o in l.obligation_set.all():
            h=H(outlinelevel=1, stylename=h3style, text=o.name)
            textdoc.text.addElement(h)
            
            if o.generic:
                p = P(text="Related Generic Obligation: ")
                v = Span(stylename=boldstyle, text=o.generic)
                p.addElement(v)
                textdoc.text.addElement(p)
            
            p = P(text="Passivity: ")
            v = Span(stylename=boldstyle, text=o.passivity)
            p.addElement(v)
            textdoc.text.addElement(p)

            p = P(text="Mode of exploitation that triggers this obligation: ")
            v = Span(stylename=boldstyle, text=o.trigger_expl)
            p.addElement(v)
            textdoc.text.addElement(p)
            
            p = P(text="Status of modification that triggers this obligation: ")
            v = Span(stylename=boldstyle, text=o.trigger_mdf)
            p.addElement(v)
            textdoc.text.addElement(p)

            if o.verbatim:
                p = P(text="Verbatim of the obligation: ")
                v = Span(text=o.verbatim)
                p.addElement(v)
                textdoc.text.addElement(p)


        p = P(stylename=itstyle, text="This license interpretation was exported from a Hermine project. https://hermine-foss.org/.")
        textdoc.text.addElement(p)

        textdoc.save(response)

        return response
    return redirect("cube:license", license_id)