# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.contrib import messages
from django.contrib.auth.decorators import (
    permission_required as permission_required_decorator,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    UpdateView,
    CreateView,
    DeleteView,
    TemplateView,
)
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import H, P, Span

from cube.forms.importers import ImportLicensesForm, ImportGenericsForm
from cube.models import License, Generic, Obligation
from cube.utils.reference import (
    LICENSE_SHARED_FIELDS,
    OBLIGATION_SHARED_FIELDS,
    join_obligations,
)
from cube.views.mixins import SearchMixin, LicenseRelatedMixin


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
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SearchMixin,
    FormErrorsToMessagesMixin,
    ListView,
    FormView,
):
    permission_required = "cube.view_license"
    model = License
    context_object_name = "licenses"
    paginate_by = 50
    form_class = ImportLicensesForm
    success_url = reverse_lazy("cube:licenses")
    search_fields = ("long_name", "spdx_id")
    template_name = "cube/license_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(obligation_count=Count("obligation")).prefetch_related(
            "obligation_set", "obligation_set__generic"
        )
        return qs

    @method_decorator(
        permission_required_decorator("cube.import_license", raise_exception=True)
    )
    def post(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().post(*args, **kwargs)


class LicenseDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "cube.view_license"
    model = License
    template_name = "cube/license_detail.html"


class LicenseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_license"
    model = License
    fields = [
        "spdx_id",
        "long_name",
        "url",
        "copyleft",
        "law_choice",
        "venue_choice",
        "status",
        "allowed",
        "allowed_explanation",
        "patent_grant",
        "foss",
        "non_commercial",
        "ethical_clause",
        "warranty",
        "liability",
        "comment",
        "verbatim",
    ]
    template_name = "cube/license_update.html"


class LicenseAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "cube.add_license"
    model = License
    fields = [
        "spdx_id",
        "long_name",
        "url",
        "copyleft",
        "law_choice",
        "venue_choice",
        "status",
        "allowed",
        "allowed_explanation",
        "patent_grant",
        "foss",
        "non_commercial",
        "ethical_clause",
        "warranty",
        "liability",
        "comment",
        "verbatim",
    ]
    template_name = "cube/license_create.html"


class LicenseDiffView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "cube.view_license"
    model = License
    template_name = "cube/license_diff.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        def display_field(obj, field):
            if hasattr(obj, f"get_{field}_display"):
                return getattr(obj, f"get_{field}_display")()
            else:
                return getattr(obj, field)

        ref_object = License.objects.using("shared").get(spdx_id=self.object.spdx_id)
        context["diff"] = [
            {
                "label": License._meta.get_field(field).verbose_name.capitalize(),
                "ref": display_field(ref_object, field),
                "local": display_field(self.object, field),
            }
            for field in LICENSE_SHARED_FIELDS
            if getattr(ref_object, field) != getattr(self.object, field)
        ]

        context["obligations_diff"] = [
            (
                obligation.name if obligation is not None else ref.name,
                "local" if not ref else "ref" if not obligation else "both",
                [
                    {
                        "label": Obligation._meta.get_field(
                            field
                        ).verbose_name.capitalize()
                        if field != "generic__name"
                        else "Generic",
                        "ref": display_field(ref, field),
                        "local": display_field(obligation, field),
                    }
                    for field in OBLIGATION_SHARED_FIELDS
                    if (getattr(ref, field) != getattr(obligation, field))
                ]
                if ref and obligation
                else None,
            )
            for obligation, ref in join_obligations(self.object, ref_object)
        ]

        return context


class PrintLicense(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "cube.view_license"
    model = License

    def render_to_response(self, context, **response_kwargs):
        filename = self.object.spdx_id + ".odt"
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
        h = H(outlinelevel=1, stylename=h1style, text=self.object.long_name)
        textdoc.text.addElement(h)
        h = H(outlinelevel=1, stylename=h2style, text=self.object.spdx_id)
        textdoc.text.addElement(h)

        p = P(text="Validation Color: ")
        v = Span(stylename=boldstyle, text=self.object.allowed)
        p.addElement(v)
        textdoc.text.addElement(p)

        if self.object.allowed_explanation is not None:
            p = P(text="Explanation: ")
            v = Span(stylename=boldstyle, text=self.object.allowed_explanation)
            p.addElement(v)
            textdoc.text.addElement(p)

        p = P(text="Copyleft: ")
        v = Span(stylename=boldstyle, text=self.object.copyleft)
        p.addElement(v)
        textdoc.text.addElement(p)

        p = P(text="Considered as Free Open Source Sofware: ")
        v = Span(stylename=boldstyle, text=self.object.foss)
        p.addElement(v)
        textdoc.text.addElement(p)

        p = P(text="Approved by OSI: ")
        v = Span(stylename=boldstyle, text=self.object.osi_approved)
        p.addElement(v)
        textdoc.text.addElement(p)

        p = P(text="Has an ethical clause: ")
        v = Span(stylename=boldstyle, text=self.object.ethical_clause)
        p.addElement(v)
        textdoc.text.addElement(p)

        if self.object.verbatim:
            p = P(text="Verbatim: ")
            value = Span(text=self.object.verbatim)
            p.addElement(value)
            textdoc.text.addElement(p)

        if self.object.comment:
            p = P(text="Comment: ")
            value = Span(stylename=boldstyle, text=self.object.comment)
            p.addElement(v)
            textdoc.text.addElement(p)

        h = H(outlinelevel=1, stylename=h2style, text="List of identified obligations")
        textdoc.text.addElement(h)

        for o in self.object.obligation_set.all():
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


class ObligationCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, LicenseRelatedMixin, CreateView
):
    permission_required = "cube.add_obligation"
    model = Obligation
    fields = ("generic", "name", "verbatim", "passivity", "trigger_expl", "trigger_mdf")
    license = None

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])


class ObligationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_obligation"
    model = Obligation
    fields = ("generic", "name", "verbatim", "passivity", "trigger_expl", "trigger_mdf")

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])


class ObligationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "cube.delete_obligation"
    model = Obligation

    def get_success_url(self):
        return reverse("cube:license", args=[self.object.license.id])


class GenericListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormErrorsToMessagesMixin,
    ListView,
    FormView,
):
    permission_required = "cube.view_generic"
    model = Generic
    template_name = "cube/generic_list.html"
    context_object_name = "generics"
    form_class = ImportGenericsForm
    success_url = reverse_lazy("cube:generics")

    @method_decorator(
        permission_required_decorator("cube.import_generic", raise_exception=True)
    )
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


class GenericDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "cube.view_generic"
    model = Generic
    context_object_name = "generic"
    template_name = "cube/generic.html"


class GenericCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "cube.add_generic"
    model = Generic
    template_name = "cube/generic_create.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse("cube:generic", args=[self.object.id])


class GenericUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_generic"
    model = Generic
    template_name = "cube/generic_update.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse("cube:generic", args=[self.object.id])


class SharedReferenceView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "cube.view_licenses"
    template_name = "cube/shared_reference.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shared"] = {
            # "version": apps.get_app_config("cube").shared_database_version,
            # "date": apps.get_app_config("cube").shared_database_date,
            "licenses": {
                "total": License.objects.using("shared"),
                "missing": License.objects.using("shared").exclude(
                    spdx_id__in=list(
                        License.objects.all().values_list("spdx_id", flat=True)
                    )
                ),
            },
            "generics": {
                "total": Generic.objects.using("shared").all(),
                "missing": Generic.objects.using("shared").exclude(
                    name__in=list(Generic.objects.all().values_list("name", flat=True))
                ),
            },
        }
        context["local"] = {
            "licenses": {
                "total": License.objects.all(),
                "missing": License.objects.exclude(
                    spdx_id__in=list(
                        License.objects.using("shared")
                        .all()
                        .values_list("spdx_id", flat=True)
                    )
                ),
            },
            "generics": {
                "total": Generic.objects.all(),
                "missing": Generic.objects.exclude(
                    name__in=list(
                        Generic.objects.using("shared")
                        .all()
                        .values_list("name", flat=True)
                    )
                ),
            },
        }

        return context
