#  SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
#
#  SPDX-License-Identifier: AGPL-3.0-only

from functools import lru_cache, reduce
from itertools import product
from types import MethodType
from typing import Iterable, List

from license_expression import get_spdx_licensing, BaseSymbol, ExpressionError


# We manually add "LicenseRef-" licenses as valid symbols
# because the license_expression library does not support them
def custom_unknown_license_symbols(self, expression, unique=True, **kwargs):
    unknown_symbols = self.super_unknown_license_symbols(expression, unique, **kwargs)
    return [
        symbol
        for symbol in unknown_symbols
        if not str(symbol).startswith("LicenseRef-")
    ]


licensing = get_spdx_licensing()
licensing.super_unknown_license_symbols = licensing.unknown_license_symbols
licensing.unknown_license_symbols = MethodType(
    custom_unknown_license_symbols, licensing
)


@lru_cache(maxsize=1024)
def has_ors(spdx_expression: str):
    parsed = licensing.parse(spdx_expression)

    if parsed is None:
        return False

    if isinstance(parsed, BaseSymbol):
        return "or-later" in str(parsed)

    if "OR" in parsed.operator:
        return True

    for sub_expression in parsed.args:
        if has_ors(sub_expression):
            return True

    return False


@lru_cache(maxsize=1024)
def is_ambiguous(spdx_expression: str):
    """
    Because of unreliable metadata, many "License1 AND License2" expressions
    actually meant to be "License1 OR License2". This function checks weither
    an expressions can be trusted or not.

    :param spdx_expression: an expression to test
    :type spdx_expression: str
    :return: whether expression needs to be confirmed
    :rtype: bool
    """
    parsed = licensing.parse(spdx_expression)
    if parsed is None or isinstance(parsed, BaseSymbol) or has_ors(spdx_expression):
        return False

    return True


@lru_cache(maxsize=1024)
def is_valid(spdx_expression: str):
    try:
        # We have to do that before validate because some ExpressionError are not
        # correctly handled by licensing.validate
        licensing.parse(spdx_expression, strict=True)
    except ExpressionError:
        return False

    info = licensing.validate(spdx_expression, strict=True)

    return len(info.errors) == 0


@lru_cache(maxsize=1024)
def get_ands_corrections(spdx_expression: str) -> Iterable[str]:
    if not is_ambiguous(spdx_expression):
        return {spdx_expression}

    return {
        str(expression)
        for expression in _get_ands_corrections_expressions(
            licensing.parse(spdx_expression)
        )
    }


def _get_ands_corrections_expressions(parsed):
    if isinstance(parsed, BaseSymbol):
        return {parsed}

    simplified = parsed.simplify()
    simplified_or_expression = reduce(lambda a, b: a | b, simplified.args).simplify()

    if all(isinstance(arg, BaseSymbol) for arg in parsed.args):
        # no sub expressions
        return {simplified, simplified_or_expression}

    combinations = list(
        product(*(_get_ands_corrections_expressions(arg) for arg in parsed.args))
    )
    and_combinations = [
        reduce(lambda a, b: a & b, combination).simplify()
        for combination in combinations
    ]
    or_combinations = [
        reduce(lambda a, b: a | b, combination).simplify()
        for combination in combinations
    ]

    return {
        simplified,
        simplified_or_expression,
        *and_combinations,
        *or_combinations,
    }


@lru_cache(maxsize=1024)
def simplified(spdx_expression: str):
    return str(licensing.parse(spdx_expression).simplify())


@lru_cache(maxsize=1024)
def explode_spdx_to_units(spdx_expr: str) -> List[str]:
    """Extract a list of every license from a SPDX valid expression.

    :param spdx_expr: A string that represents a valid SPDX expression. (Like ")
    :type spdx_expr: string
    :return: A list of valid SPDX licenses contained in the expression.
    :rtype: list
    """
    parsed = licensing.parse(spdx_expr)
    if parsed is None:
        return []
    return sorted(list(parsed.objects))
