#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only
from types import MethodType

from django.core.exceptions import ValidationError
from license_expression import get_spdx_licensing

licensing = get_spdx_licensing()


def custom_unknown_license_symbols(self, expression, unique=True, **kwargs):
    unknown_symbols = self.super_unknown_license_symbols(expression, unique, **kwargs)
    return [
        symbol
        for symbol in unknown_symbols
        if not str(symbol).startswith("LicenseRef-")
    ]


licensing.super_unknown_license_symbols = licensing.unknown_license_symbols
licensing.unknown_license_symbols = MethodType(
    custom_unknown_license_symbols, licensing
)


def validate_spdx_expression(spdx_expression: str):
    info = licensing.validate(spdx_expression)
    if len(info.errors) > 0:
        raise ValidationError(
            f"{spdx_expression} is not a valid SPDX expression : {', '.join(info.errors)}"
        )
