#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.db.models import Count
from django.forms import Form, ChoiceField, Select

from cube.models import Release, Usage, Exploitation


class ReleaseExploitationForm(Form):
    def __init__(self, instance: Release, *args, **kwargs):
        self.release = instance
        self.scopes = self.release.usage_set.values_list("project", "scope").annotate(
            count=Count("*")
        )
        super().__init__(*args, **kwargs)

        for project, scope, count in self.scopes:
            self.fields[str(project) + str(scope)] = ChoiceField(
                choices=Usage.EXPLOITATION_CHOICES,
                widget=Select(attrs={"class": "select"}),
                label=f"{project or '(project undefined)'} - {scope} ({count} components)",
            )

            try:
                self.initial[project + scope] = self.release.exploitations.get(
                    project=project, scope=scope
                ).exploitation
            except Exploitation.DoesNotExist:
                pass

    def save(self):
        for project, scope, _ in self.scopes:
            exploitation_type = self.cleaned_data[project + scope]
            Exploitation.objects.update_or_create(
                release=self.release,
                project=project,
                scope=scope,
                defaults={"exploitation": exploitation_type},
            )

        return self.release
