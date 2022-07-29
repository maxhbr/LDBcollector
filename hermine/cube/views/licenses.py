# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import H, P, Span

from cube.forms import ImportLicensesForm, ImportGenericsForm
from cube.models import License, Generic
from cube.views.mixins import SearchMixin


class FormErrorsToMessagesMixin:
    def form_invalid(self, form):
        for field, errs in form.errors.items():
            for err in errs:
                messages.add_message(self.request, messages.ERROR, err)
        return super().form_invalid(form)

    def form_valid(self, form):
        try:
            form.save()
        except ValidationError as e:
            messages.add_message(self.request, messages.ERROR, e.message)
            return super().form_invalid(form)
        messages.add_message(self.request, messages.SUCCESS, "File imported.")
        return super().form_valid(form)


class LicensesListView(
    LoginRequiredMixin, SearchMixin, FormErrorsToMessagesMixin, ListView, FormView
):
    model = License
    context_object_name = "licenses"
    paginate_by = 50
    form_class = ImportLicensesForm
    success_url = reverse_lazy("cube:licenses")
    search_fields = ("long_name", "spdx_id")

    def post(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().post(*args, **kwargs)


class LicenseDetailView(LoginRequiredMixin, DetailView):
    model = License
    context_object_name = "license"
    template_name = "cube/license.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orphan_obligations = self.object.obligation_set.filter(generic__isnull=True)
        generic_obligations = self.object.obligation_set.filter(
            generic__in_core=False
        ).order_by("generic__id")
        core_obligations = self.object.obligation_set.filter(
            generic__in_core=True
        ).order_by("generic__id")

        context.update(
            {
                "orphan_obligations": orphan_obligations,
                "obligations_in_generic": generic_obligations,
                "obligations_in_core": core_obligations,
            }
        )
        return context


# def export_licenses(request):
#     """An export function that uses the License Serializer on all the licenses.
#     Effective, but using the the other one which calls the API might allow to handle
#     specific cases such as access restrictions
#     """
#     filename = "licenses.json"
#     serializer = LicenseSerializer
#     data = serializer(License.objects.all(), many=True).data
#     with open(filename, "w+"):
#         response = HttpResponse(
#             json.dumps(data, indent=4), content_type="application/json"
#         )
#         response["Content-Disposition"] = "attachment; filename=%s" % filename
#         return response


def print_license(request, license_id):
    license_instance = get_object_or_404(License, pk=license_id)
    filename = license_instance.spdx_id + ".odt"
    with open(filename, "w+"):
        response = HttpResponse(content_type="application/vnd.oasis.opendocument.text")
        response["Content-Disposition"] = "attachment; filename=%s" % filename

        textdoc = OpenDocumentText()
        s = textdoc.styles

        h1style = Style(name="Heading 1", family="paragraph")
        h1style.addElement(
            TextProperties(attributes={"fontsize": "24pt", "fontweight": "bold"})
        )
        s.addElement(h1style)
        h1style.addElement(ParagraphProperties(attributes={"marginbottom": "1cm"}))
        h2style = Style(name="Heading 2", family="paragraph")
        h2style.addElement(
            TextProperties(attributes={"fontsize": "18pt", "fontweight": "bold"})
        )
        h2style.addElement(
            ParagraphProperties(
                attributes={"marginbottom": "0.6cm", "margintop": "0.4cm"}
            )
        )
        s.addElement(h2style)

        h3style = Style(name="Heading 3", family="paragraph")
        h3style.addElement(
            TextProperties(attributes={"fontsize": "14pt", "fontweight": "bold"})
        )
        h3style.addElement(
            ParagraphProperties(
                attributes={"marginbottom": "0.2cm", "margintop": "0.4cm"}
            )
        )

        s.addElement(h3style)

        itstyle = Style(name="Italic", family="paragraph")
        itstyle.addElement(TextProperties(attributes={"textemphasize": "true"}))
        itstyle.addElement(ParagraphProperties(attributes={"margintop": "3cm"}))

        s.addElement(itstyle)

        # An automatic style
        boldstyle = Style(name="Bold", family="text")
        boldprop = TextProperties(fontweight="bold")
        boldstyle.addElement(boldprop)
        textdoc.automaticstyles.addElement(boldstyle)

        textdoc.automaticstyles.addElement(itstyle)

        # Text
        h = H(outlinelevel=1, stylename=h1style, text=license_instance.long_name)
        textdoc.text.addElement(h)
        h = H(outlinelevel=1, stylename=h2style, text=license_instance.spdx_id)
        textdoc.text.addElement(h)

        p = P(text="Validation Color: ")
        v = Span(stylename=boldstyle, text=license_instance.color)
        p.addElement(v)
        textdoc.text.addElement(p)

        if license_instance.color_explanation is not None:
            p = P(text="Explanation: ")
            v = Span(stylename=boldstyle, text=license_instance.color_explanation)
            p.addElement(v)
            textdoc.text.addElement(p)

        p = P(text="Copyleft: ")
        v = Span(stylename=boldstyle, text=license_instance.copyleft)
        p.addElement(v)
        textdoc.text.addElement(p)

        p = P(text="Considered as Free Open Source Sofware: ")
        v = Span(stylename=boldstyle, text=license_instance.foss)
        p.addElement(v)
        textdoc.text.addElement(p)

        p = P(text="Approved by OSI: ")
        v = Span(stylename=boldstyle, text=license_instance.osi_approved)
        p.addElement(v)
        textdoc.text.addElement(p)

        p = P(text="Has an ethical clause: ")
        v = Span(stylename=boldstyle, text=license_instance.ethical_clause)
        p.addElement(v)
        textdoc.text.addElement(p)

        if license_instance.verbatim:
            p = P(text="Verbatim: ")
            value = Span(text=license_instance.verbatim)
            p.addElement(value)
            textdoc.text.addElement(p)

        if license_instance.comment:
            p = P(text="Comment: ")
            value = Span(stylename=boldstyle, text=license_instance.comment)
            p.addElement(v)
            textdoc.text.addElement(p)

        h = H(outlinelevel=1, stylename=h2style, text="List of identified obligations")
        textdoc.text.addElement(h)

        for o in license_instance.obligation_set.all():
            h = H(outlinelevel=1, stylename=h3style, text=o.name)
            textdoc.text.addElement(h)
            generic = o.generic

            if generic:
                p = P(text="Related Generic Obligation: ")
                v = Span(stylename=boldstyle, text=generic)
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

        p = P(
            stylename=itstyle,
            text="This license interpretation was exported from a Hermine project."
            + " https://hermine-foss.org/.",
        )
        textdoc.text.addElement(p)

        textdoc.save(response)

        return response
    return redirect("cube:license", license_id)


class GenericListView(
    LoginRequiredMixin, FormErrorsToMessagesMixin, ListView, FormView
):
    model = Generic
    context_object_name = "generics"
    form_class = ImportGenericsForm
    success_url = reverse_lazy("cube:generics")

    def post(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().post(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            "generics_incore": self.object_list.filter(in_core=True),
            "generics_outcore": self.object_list.filter(in_core=False),
        }
        context.update(**kwargs)
        return super().get_context_data(object_list=object_list, **context)


class GenericDetailView(LoginRequiredMixin, DetailView):
    model = Generic
    context_object_name = "generic"
    template_name = "cube/generic.html"
