# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only
from django.contrib.auth.models import User

from cube.models.components import Component, Version, Usage, Funding
from cube.models.licenses import License, LicensePolicy, Team, Generic, Obligation
from cube.models.policy import (
    LicenseCuration,
    LicenseChoice,
    Derogation,
)
from cube.models.products import (
    Product,
    Category,
    Release,
    Exploitation,
)

# Constant for Usage and Derogation models
