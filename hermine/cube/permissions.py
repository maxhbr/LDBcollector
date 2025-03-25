#  SPDX-FileCopyrightText: 2025 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from rest_framework.permissions import DjangoModelPermissions, BasePermission


class ReadWriteDjangoModelPermissions(DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class UpdateSBOMPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.user.has_perms(["cube.change_release_bom"]):
            return True
        return False
