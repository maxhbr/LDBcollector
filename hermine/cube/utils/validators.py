#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.core.exceptions import ValidationError
from .spdx import licensing, has_ors


def validate_spdx_expression(spdx_expression: str):
    info = licensing.validate(spdx_expression)
    if len(info.errors) > 0:
        raise ValidationError(
            f"{spdx_expression} is not a valid SPDX expression : {', '.join(info.errors)}"
        )


def validate_no_ors_expression(spdx_expression: str):
    if has_ors(spdx_expression):
        raise ValidationError("Expression still contains a license choice")
