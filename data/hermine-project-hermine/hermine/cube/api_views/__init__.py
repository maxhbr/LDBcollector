# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

from rest_framework.routers import APIRootView

from .components import *
from .licenses import *
from .policy import *
from .products import *


class RootView(APIRootView):
    """Documentation for the API is available through Swagger at /api-doc"""

    pass
