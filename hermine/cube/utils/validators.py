#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from django.core.exceptions import ValidationError
from license_expression import ExpressionError

from .spdx import licensing, has_ors


def validate_spdx_expression(spdx_expression: str):
    try:
        # We have to do that before validate because some ExpressionError are not
        # correctly handled by licensing.validate
        licensing.parse(spdx_expression, strict=True)
    except ExpressionError as e:
        raise ValidationError(f"{spdx_expression} is not a valid SPDX expression : {e}")

    info = licensing.validate(spdx_expression, strict=True)
    if len(info.errors) > 0:
        raise ValidationError(
            f"{spdx_expression} is not a valid SPDX expression : {', '.join(info.errors)}"
        )


def validate_no_ors_expression(spdx_expression: str):
    if has_ors(spdx_expression):
        raise ValidationError("Expression still contains a license choice")
