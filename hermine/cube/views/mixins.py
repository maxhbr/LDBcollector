#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from functools import reduce

from django.db.models import Q, Count
from django.forms import Form, CharField
from django.shortcuts import get_object_or_404
from django.urls import reverse

from cube.models import License, Release, Exploitation


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
                        Q(**{f"{field}__contains": self.query})
                        for field in self.search_fields
                    ),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.query:
            context.update({"query": self.query})

        return context


class LicenseRelatedMixin:
    def dispatch(self, request, *args, **kwargs):
        self.license = get_object_or_404(License, id=kwargs["license_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self):
        context = super().get_context_data()
        context["license"] = self.license
        return context

    def form_valid(self, form):
        form.instance.license = self.license
        return super().form_valid(form)


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


class ReleaseExploitationRedirectMixin:
    def get_success_url(self):
        if self.request.GET.get("redirect") == "validation":
            return reverse("cube:release_validation", args=[self.release.id])
        if self.request.GET.get("redirect") == "exploitations":
            return reverse("cube:release_exploitations", args=[self.release.id])
        return reverse("cube:release_summary", args=[self.release.id])


class ReleaseExploitationFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scopes_in_release = (
            self.release.usage_set.values("project", "scope")
            .annotate(count=Count("*"))
            .values("project", "scope", "count")
            .order_by("project", "scope")
        )
        exploitations = self.get_queryset().values(
            "project", "scope", "exploitation", "id"
        )
        explicit_exploitations = dict()
        for key, value in Exploitation._meta.get_field("exploitation").choices:
            explicit_exploitations[key] = value

        full_exploitations = dict()
        for scope_in_release in scopes_in_release:
            full_scope = scope_in_release["project"] + scope_in_release["scope"]
            full_exploitations[full_scope] = dict()
            full_exploitations[full_scope]["scope"] = scope_in_release["scope"]
            full_exploitations[full_scope]["project"] = scope_in_release["project"]
            full_exploitations[full_scope]["count"] = scope_in_release["count"]
        for exploitation in exploitations:
            full_scope = exploitation["project"] + exploitation["scope"]
            print("exploitation,", full_scope)
            if full_scope in full_exploitations:
                full_exploitations[full_scope]["exploitation"] = explicit_exploitations[
                    exploitation["exploitation"]
                ]
                full_exploitations[full_scope]["exploitation_id"] = exploitation["id"]
            else:
                full_exploitations[full_scope] = dict()
                full_exploitations[full_scope]["scope"] = exploitation["scope"]
                full_exploitations[full_scope]["project"] = exploitation["project"]
                full_exploitations[full_scope]["exploitation"] = explicit_exploitations[
                    exploitation["exploitation"]
                ]
                full_exploitations[full_scope]["exploitation_id"] = exploitation["id"]

        context["full_exploitations"] = list(full_exploitations.values())
        return context
