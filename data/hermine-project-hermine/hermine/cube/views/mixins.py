#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from functools import reduce

from django.db.models import Q, Count, Subquery, OuterRef, F, Value
from django.db.models.functions import Coalesce
from django.forms import Form, CharField
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from cube.models import License, Release
from cube.utils.reference import is_shared_reference_loaded


class SearchForm(Form):
    search = CharField(required=False)


class SearchMixin:
    """
    Mixin to add search capabilities to a view.

    To use it, you must define a `search_fields` attribute on your view.
    It must be a list of fields to search in.
    The mixin will add a `query` attribute to the context, containing the
    search query.
    """

    search_fields = None
    query = None

    def get_queryset(self, *args, **kwargs):
        search_form = SearchForm(self.request.GET)

        if not search_form.is_valid() or not (
            query := search_form.cleaned_data.get("search")
        ):
            return super().get_queryset(*args, **kwargs)

        self.query = query
        return (
            super()
            .get_queryset(*args, **kwargs)
            .filter(
                reduce(
                    lambda a, b: a | b,
                    (
                        Q(**{f"{field}__icontains": query})
                        for field in self.search_fields
                    ),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"search_form": SearchForm(self.request.GET)})

        return context


class CreateLicenseRelatedMixin:
    """
    To be used with ModelForm/CreateView on models that have a ForeignKey to License

    The ForeignKey field can most of the time completely be ommited of the ModelForm
    field list, as it is automatically added before validation by this mixin.

    The only exception is if the ForeignKey field is part of a multifield constraint (like
    unique together), in which case it should be included in the form as a hidden field
    for model validations to run correctly.
    """

    related_field_name = "license"

    def dispatch(self, request, *args, **kwargs):
        self.license = get_object_or_404(License, id=kwargs["license_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """
        Only used in the hidden field case
        """
        return {self.related_field_name: self.license}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["license"] = self.license
        return context

    def form_valid(self, form):
        setattr(form.instance, self.related_field_name, self.license)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "cube:license_detail",
            args=[getattr(self.object, self.related_field_name).id],
        )


class SaveAuthorMixin:
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ReleaseContextMixin:
    release = None

    def dispatch(self, *args, **kwargs):
        self.release = Release.objects.get(pk=self.kwargs["release_pk"])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["release"] = self.release
        return context


class QuerySuccessUrlMixin:
    def _get_from_path(self):
        candidate = self.request.GET.get("from")
        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return candidate
        return None

    def get_default_success_url(self):
        if hasattr(self, "success_url") and self.success_url is not None:
            return self.success_url

        try:
            return super().get_success_url()
        except AttributeError:
            raise NotImplementedError(
                "You must implement get_default_success_url() or success_url"
            )

    def get_success_url(self):
        return self._get_from_path() or self.get_default_success_url()

    def get_cancel_url(self):
        return self._get_from_path() or self.get_default_success_url()

    def get_context_data(self, **kwargs):
        kwargs.setdefault("cancel_url", self.get_cancel_url())
        return super().get_context_data(**kwargs)


class ReleaseExploitationFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # List existing scopes
        scopes = list(
            self.object.usage_set.values("project", "scope")
            .annotate(count=Count("*"))
            .values("project", "scope", "count")
            .order_by("project", "scope")
        )

        # Attach existing exploitations to scopes
        for scope in scopes:
            scope["exploitation"] = self.object.exploitations.filter(
                project=scope["project"], scope=scope["scope"]
            ).first()

        # Add exploitations with no usages
        for exploitation in self.object.exploitations.filter(
            *[(~Q(project=scope["project"], scope=scope["scope"])) for scope in scopes]
        ):
            scopes.append(
                {
                    "exploitation": exploitation,
                    "count": 0,
                    "project": exploitation.project,
                    "scope": exploitation.scope,
                }
            )

        # Usages with ad-hoc exploitation
        exploitation_rules_subquery = self.object.exploitations.filter(
            project=OuterRef("project"), scope=OuterRef("scope")
        ).values("exploitation")[:1]
        adhoc_exploitations = (
            self.object.usage_set.annotate(
                registered_exploitation=Coalesce(
                    Subquery(exploitation_rules_subquery), Value("")
                )
            )
            .exclude(exploitation=F("registered_exploitation"))
            .exclude(exploitation="")
        )

        context["exploitation_scopes"] = scopes
        context["adhoc_exploitations"] = adhoc_exploitations

        return context


class SharedDataRequiredMixin:
    def dispatch(self, *args, **kwargs):
        if not is_shared_reference_loaded():
            raise Http404("Shared data not loaded")
        return super().dispatch(*args, **kwargs)
