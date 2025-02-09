# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.contrib import messages
from django.contrib.auth.decorators import (
    permission_required as permission_required_decorator,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError, SuspiciousOperation
from django.db.models import Count
from django.db.models.functions import Lower
from django.forms import modelform_factory
from django.http import HttpResponse
from django.shortcuts import redirect
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
from cube.forms.licenses import (
    ObligationGenericDiffForm,
    CopyReferenceLicensesForm,
    CopyReferenceGenericsForm,
    CopyReferenceObligationForm,
    SyncEverythingFromReferenceForm,
)
from cube.models import License, Generic, Obligation
from cube.utils.reference import (
    LICENSE_SHARED_FIELDS,
    OBLIGATION_SHARED_FIELDS,
    join_obligations,
    GENERIC_SHARED_FIELDS,
)
from cube.views.mixins import SearchMixin, LicenseRelatedMixin, SharedDataRequiredMixin


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
    ordering = [Lower("spdx_id")]
    form_class = ImportLicensesForm
    success_url = reverse_lazy("cube:license_list")
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


class LicenseDataUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_license"
    model = License
    fields = LICENSE_SHARED_FIELDS
    template_name = "cube/license_update.html"
    obligations = []

    # We override get_object to handle the "duplicate" action
    # We also store the obligations to duplicate them later
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if "duplicate" in self.request.POST:
            self.obligations = list(obj.obligation_set.all())
            obj.pk = None
            obj.long_name = obj.long_name + " (copy)"
        return obj

    def form_valid(self, form):
        if "duplicate" in self.request.POST:
            self.object.save()
            for obligation in self.obligations:
                obligation.pk = None
                obligation.license = self.object
                obligation.save()
            return redirect(self.get_success_url())
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object.pk = self.kwargs[
            "pk"
        ]  # we need to restore it back to the original value
        return super().form_invalid(form)


class LicensePolicyUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_license"
    model = License
    form_class = modelform_factory(License, exclude=LICENSE_SHARED_FIELDS)
    template_name = "cube/license_update_policy.html"


class LicenseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shared_fields"] = []
        context["policy_fields"] = []
        for field in context["form"]:
            if field.name in LICENSE_SHARED_FIELDS:
                context["shared_fields"].append(field)
            else:
                context["policy_fields"].append(field)
        return context


class LicenseDiffView(
    LoginRequiredMixin, PermissionRequiredMixin, SharedDataRequiredMixin, DetailView
):
    permission_required = "cube.view_license"
    model = License
    template_name = "cube/license_diff.html"

    def display_field(self, obj, field):
        if hasattr(obj, f"get_{field}_display"):
            return getattr(obj, f"get_{field}_display")()
        else:
            return getattr(obj, field)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ref_object = License.objects.using("shared").get(spdx_id=self.object.spdx_id)
        context["diff"] = [
            {
                "name": field,
                "label": License._meta.get_field(field).verbose_name.capitalize(),
                "ref": self.display_field(ref_object, field),
                "local": self.display_field(self.object, field),
                "form_field": next(
                    iter(
                        modelform_factory(License, fields=[field])(
                            initial={field: getattr(ref_object, field)},
                            instance=self.object,
                        )
                    )
                ),
            }
            for field in LICENSE_SHARED_FIELDS
            if getattr(ref_object, field) != getattr(self.object, field)
        ]

        context["obligations_diff"] = []
        for obligation, ref in join_obligations(self.object, ref_object):
            obligation_name = obligation.name if obligation is not None else ref.name
            sides = "local" if not ref else "ref" if not obligation else "both"

            if sides == "local":
                context["obligations_diff"].append(
                    (obligation_name, sides, obligation.id, None)
                )
                continue

            if sides == "ref":
                context["obligations_diff"].append(
                    (obligation_name, sides, ref.id, None)
                )
                continue

            fields = [
                {
                    "name": field,
                    "label": Obligation._meta.get_field(
                        field
                    ).verbose_name.capitalize(),
                    "ref": self.display_field(ref, field),
                    "local": self.display_field(obligation, field),
                    "form_field": next(
                        iter(
                            modelform_factory(Obligation, fields=[field])(
                                initial={field: getattr(ref, field)},
                                instance=self.object,
                            )
                        )
                    ),
                }
                for field in OBLIGATION_SHARED_FIELDS
                if (getattr(ref, field) != getattr(obligation, field))
            ]

            if (
                obligation.generic
                and ref.generic
                and ref.generic.name != obligation.generic.name
            ):
                fields.append(
                    {
                        "name": "generic",
                        "label": Obligation._meta.get_field(
                            "generic"
                        ).verbose_name.capitalize(),
                        "ref": ref.generic.name,
                        "local": obligation.generic.name,
                        "form_field": next(
                            iter(
                                ObligationGenericDiffForm(
                                    initial={"generic": ref.generic},
                                    instance=self.object,
                                )
                            )
                        ),
                    }
                )

            context["obligations_diff"].append(
                (obligation_name, sides, obligation.id, fields)
            )

        return context


class LicenseDiffUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_license"
    model = License

    def get_form_class(self):
        return modelform_factory(License, fields=[self.kwargs["field"]])

    def get_success_url(self):
        return reverse("cube:license_diff", kwargs={"pk": self.object.pk})


class LicensePrintView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
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

            p = P(text="Passive/Active: ")
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
        return reverse("cube:license_detail", args=[self.object.license.id])


class ObligationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_obligation"
    model = Obligation
    fields = ("generic", "name", "verbatim", "passivity", "trigger_expl", "trigger_mdf")

    def get_success_url(self):
        return reverse("cube:license_detail", args=[self.object.license.id])


class ObligationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "cube.delete_obligation"
    model = Obligation

    def get_success_url(self):
        return reverse("cube:license_detail", args=[self.object.license.id])


class ObligationDiffUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_obligation"
    model = Obligation
    fields = ("verbatim",)

    def get_success_url(self):
        return reverse("cube:license_diff", args=[self.object.license.id])

    def get_form_class(self):
        if self.kwargs["field"] == "generic":
            return ObligationGenericDiffForm
        return modelform_factory(Obligation, fields=[self.kwargs["field"]])


class ObligationsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "cube.view_license"
    model = Obligation
    context_object_name = "obligations"

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(generic__exact=None).order_by("license__spdx_id")
        return qs


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
    success_url = reverse_lazy("cube:generic_list")

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
    template_name = "cube/generic_detail.html"


class GenericCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "cube.add_generic"
    model = Generic
    template_name = "cube/generic_create.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse("cube:generic_detail", args=[self.object.id])


class GenericUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_generic"
    model = Generic
    template_name = "cube/generic_update.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse("cube:generic_detail", args=[self.object.id])


class GenericDiffView(
    LoginRequiredMixin, PermissionRequiredMixin, SharedDataRequiredMixin, DetailView
):
    permission_required = "cube.view_generic"
    model = Generic
    template_name = "cube/generic_diff.html"

    def display_field(self, obj, field):
        if hasattr(obj, f"get_{field}_display"):
            return getattr(obj, f"get_{field}_display")()
        else:
            return getattr(obj, field)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ref_object = Generic.objects.using("shared").get(name=self.object.name)
        context["diff"] = [
            {
                "name": field,
                "label": Generic._meta.get_field(field).verbose_name.capitalize(),
                "ref": self.display_field(ref_object, field),
                "local": self.display_field(self.object, field),
                "form_field": next(
                    iter(
                        modelform_factory(Generic, fields=[field])(
                            initial={field: getattr(ref_object, field)},
                            instance=self.object,
                        )
                    )
                ),
            }
            for field in GENERIC_SHARED_FIELDS
            if getattr(ref_object, field) != getattr(self.object, field)
        ]

        return context


class GenericDiffUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "cube.change_generic"
    model = Generic

    def get_success_url(self):
        return reverse("cube:generic_diff", args=[self.object.id])

    def get_form_class(self):
        return modelform_factory(Generic, fields=[self.kwargs["field"]])


class SharedReferenceView(
    LoginRequiredMixin, PermissionRequiredMixin, SharedDataRequiredMixin, TemplateView
):
    permission_required = "cube.view_license"
    template_name = "cube/shared_reference.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        licenses = list(License.objects.all())
        context["licenses"] = {
            "total": len(licenses),
            "diff": len([lic for lic in licenses if lic.reference_diff]),
            "only_local": License.objects.exclude(
                spdx_id__in=list(
                    License.objects.using("shared")
                    .all()
                    .values_list("spdx_id", flat=True)
                )
            ).count(),
            "only_shared": License.objects.using("shared")
            .exclude(spdx_id__in=(lic.spdx_id for lic in licenses))
            .count(),
        }

        generics = list(Generic.objects.all())
        context["generics"] = {
            "total": len(generics),
            "diff": len([gen for gen in generics if gen.reference_diff]),
            "only_local": Generic.objects.exclude(
                name__in=list(
                    Generic.objects.using("shared").all().values_list("name", flat=True)
                )
            ).count(),
            "only_shared": Generic.objects.using("shared")
            .exclude(name__in=(gen.name for gen in generics))
            .count(),
        }

        return context


class CopyReferenceLicensesView(
    LoginRequiredMixin, PermissionRequiredMixin, SharedDataRequiredMixin, FormView
):
    permission_required = "cube.change_license"
    form_class = CopyReferenceLicensesForm
    success_url = reverse_lazy("cube:shared_reference")

    def form_invalid(self, form):
        return super().form_valid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CopyReferenceGenericsView(
    LoginRequiredMixin, PermissionRequiredMixin, SharedDataRequiredMixin, FormView
):
    permission_required = "cube.change_generic"
    form_class = CopyReferenceGenericsForm
    success_url = reverse_lazy("cube:shared_reference")

    def form_invalid(self, form):
        return super().form_valid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CopyReferenceObligationView(
    LoginRequiredMixin, PermissionRequiredMixin, SharedDataRequiredMixin, FormView
):
    permission_required = "cube.change_license"
    form_class = CopyReferenceObligationForm

    def form_invalid(self, form):
        raise SuspiciousOperation("Form is invalid")

    def form_valid(self, form):
        obligation = form.save()
        return redirect(reverse("cube:license_diff", args=[obligation.license.id]))


class SyncEverythingFromReferenceView(
    LoginRequiredMixin, PermissionRequiredMixin, SharedDataRequiredMixin, FormView
):
    permission_required = "cube.change_license"
    form_class = SyncEverythingFromReferenceForm
    success_url = reverse_lazy("cube:shared_reference")

    def form_invalid(self, form):
        return super().form_valid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
