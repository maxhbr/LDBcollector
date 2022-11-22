#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from functools import reduce

from django.db.models import Q
from django.forms import Form, CharField
from django.shortcuts import get_object_or_404

from cube.models import License


class SearchForm(Form):
    search = CharField(required=False)


class SearchMixin:
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
