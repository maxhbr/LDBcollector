#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from functools import reduce

from django.db.models import Q, Count, Subquery, OuterRef, F, Value
from django.db.models.functions import Coalesce
from django.forms import Form, CharField
from django.shortcuts import get_object_or_404
from django.urls import reverse

from cube.models import License, Release


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
        return reverse("cube:release_summary", args=[self.release.id])


class ReleaseExploitationFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Existing scopes
        scopes = list(
            self.release.usage_set.values("project", "scope")
            .annotate(count=Count("*"))
            .values("project", "scope", "count")
            .order_by("project", "scope")
        )

        # Attach existing exploitations to scopes
        for scope in scopes:
            scope["exploitation"] = self.release.exploitations.filter(
                project=scope["project"], scope=scope["scope"]
            ).first()

        # Add exploitations with no usages
        for exploitation in self.release.exploitations.filter(
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

        # Usages with custom scopes
        exploitation_rules_subquery = self.release.exploitations.filter(
            project=OuterRef("project"), scope=OuterRef("scope")
        ).values("exploitation")[:1]
        custom_scopes = (
            self.release.usage_set.annotate(
                registered_exploitation=Coalesce(
                    Subquery(exploitation_rules_subquery), Value("")
                )
            )
            .exclude(exploitation=F("registered_exploitation"))
            .exclude(exploitation="")
        )

        context["exploitation_scopes"] = scopes
        context["custom_scopes"] = custom_scopes

        return context
