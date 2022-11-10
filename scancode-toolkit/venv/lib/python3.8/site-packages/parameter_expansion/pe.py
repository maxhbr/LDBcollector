#!/usr/bin/env python

"""
Given a string, expand that string using POSIX [parameter expansion][1].

Most nested expression expansions should be working now, but YMMV. Things such
as in `${foo:-${bar:-$baz}}` should work fine.

Also support some level of Bash extensions to expansion [3]:
- pattern substitution with `${foo/bar/baz}` (but only plain strings and not patterns)
- substring expansion with `${foo:4:2}


## Limitations

(Pull requests to remove limitations are welcome.)

- Only ASCII alphanumeric characters and underscores are supported in parameter
names. (Per POSIX, parameter names may not begin with a numeral.)

- Assignment expansions do not mutate the real environment.

- For simplicity's sake, this implementation uses fnmatch instead of
completely reimplementing [POSIX pattern matching][2]

- Comments in strings are unsupported.

[1]: http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_06_02
[2]: http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_13
[3]: https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
"""

import logging
import os
import re
import sys
from fnmatch import fnmatchcase
from itertools import groupby, takewhile
from shlex import shlex

# Tracing flags: set to True to enable debug trace
TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


def logger_debug(*args):
    logger.debug(" ".join(a if isinstance(a, str) else repr(a) for a in args))


def expand(s, env=None, strict=False):
    """Expand the string using POSIX parameter expansion rules.
    Uses the provided environment dict or the actual environment.
    If strict is True, raise a ParameterExpansionNullError on missing
    env variable.

    For example::
    >>> env = {"foo": "bar", "foobar": "BAR"}
    >>> expand("${foo${foo}}", env=env, strict=True)
    'BAR'
    """
    if env is None:
        env = dict(os.environ)

    # Loop until fully expanded or no longer expanding anything
    #  - expand simple parameters (i.e. these without a shell expression)
    #  - get plain expressions and expand them (i.e. non-nested expressions)
    # Eventually all complex expressions are composed of simple expressions and
    # will be expanded this way.
    while True:
        # use this to track if we are expanding in this cycle
        original_s = s
        s = expand_simple(s, env)

        plain_exps = get_plain_expressions(s)

        if not plain_exps:
            break

        for plain in plain_exps:

            expanded = "".join(expand_tokens(plain, env=env, strict=strict))
            logger_debug("expand: plain:", plain, "expanded:", expanded)
            s = s.replace(plain, expanded)
            s = expand_simple(s, env)

        # check if we expanded or not in this cycle and exit
        has_expanded = s != original_s
        if not has_expanded:
            break

    logger_debug("expand: final", s)
    return s


class ParameterExpansionNullError(LookupError):
    pass


class ParameterExpansionParseError(Exception):
    pass


def expand_tokens(s, env, strict=False):
    tokens = tokenize(s)
    while True:
        try:
            before_dollar = "".join(takewhile(lambda t: t != "$", tokens))
            logger_debug("expand_tokens: before_dollar:", repr(before_dollar))
            yield before_dollar
            sigil = follow_sigil(tokens, env, strict)
            logger_debug("expand_tokens: sigil:", repr(sigil))
            yield sigil
        except StopIteration:
            return


def tokenize(s):
    """Yield token strings lexed from the shell string s."""
    shl = shlex(s, posix=True)
    shl.commenters = ""
    shl.whitespace = ""
    for grouped, group in groupby(shl, key=is_whitespace):
        # we group contiguous whitespaces in one string
        if grouped:
            yield "".join(group)
        else:
            yield from group


_get_non_nested_expressions = re.compile(r"(\$\{[^${}]+\})").findall


def get_plain_expressions(s):
    """Return a list of plain, non-nested shell expressions found in the shell
    string s. These are shell expressions that do not further contain a nested
    expression and can therefore be resolved indenpendently.

    For example::
    >>> get_plain_expressions("${_pyname%${_pyname#?}}")
    ['${_pyname#?}']
    """
    return _get_non_nested_expressions(s)


def follow_sigil(shl, env, strict=False):
    param = next(shl)
    if param == "{":
        # note: we consume the iterator here on purpose
        inside_sigils = list(takewhile(lambda t: t != "}", shl))
        logger_debug("follow_sigil: inside_sigils:", inside_sigils)
        # note: downstream code expects an iterator with a next() and not a list
        inside_sigils = iter(inside_sigils)
        return follow_brace(inside_sigils, env, strict)
    expanded = env.get(param)
    if strict and expanded is None:
        raise ParameterExpansionNullError(param)
    return expanded or ""


def expand_simple(s, env):
    """Expand a string containing shell variable substitutions.
    This expands the forms $variable and ${variable} only.
    Non-existent variables are left unchanged.
    Uses the provided environment dict.
    Similar to ``os.path.expandvars``.
    """
    env_by_decreasing_name_length = sorted(
        env.items(),
        # [0] is the name.  minus its length gets the longest first.
        key=lambda name_value: -len(name_value[0]),
    )

    for name, value in env_by_decreasing_name_length:
        s = s.replace(f"${name}", value)
        name = "{" + name + "}"
        s = s.replace(f"${name}", value)
    return s


def remove_affix(subst, shl, suffix=True):
    """
    From http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_13

       > The following four varieties of parameter expansion provide for
       substring processing. In each case, pattern matching notation (see
       Pattern Matching Notation), rather than regular expression notation,
       shall be used to evaluate the patterns. If parameter is '*' or '@', the
       result of the expansion is unspecified. Enclosing the full parameter
       expansion string in double-quotes shall not cause the following four
       varieties of pattern characters to be quoted, whereas quoting characters
       within the braces shall have this effect.

       > ${parameter%word} : Remove Smallest Suffix Pattern. The word shall be
       expanded to produce a pattern. The parameter expansion shall then result
       in parameter, with the smallest portion of the suffix matched by the
       pattern deleted.

       > ${parameter%%word} : Remove Largest Suffix Pattern. The word shall be
       expanded to produce a pattern. The parameter expansion shall then result
       in parameter, with the largest portion of the suffix matched by the
       pattern deleted.

       > ${parameter#word} : Remove Smallest Prefix Pattern. The word shall be
       expanded to produce a pattern. The parameter expansion shall then result
       in parameter, with the smallest portion of the prefix matched by the
       pattern deleted.

       > ${parameter##word} : Remove Largest Prefix Pattern. The word shall be
       expanded to produce a pattern. The parameter expansion shall then result
       in parameter, with the largest portion of the prefix matched by the
       pattern deleted.
    """
    largest = False
    # at this stage shl has already been trimmed from its leading % or # so
    # we check for a second % or # to find if we need a largest match or not
    pat = "".join(shl)
    if pat.startswith("%" if suffix else "#"):
        largest = True
        pat = pat[1:]
    size = len(subst)
    indices = range(0, size)
    if largest != suffix:
        indices = reversed(indices)
    if suffix:
        for i in indices:
            if fnmatchcase(subst[i:], pat):
                return subst[:i]
        return subst
    else:
        for i in indices:
            if fnmatchcase(subst[:i], pat):
                return subst[i:]
        return subst


def remove_suffix(subst, shl):
    return remove_affix(subst=subst, shl=shl, suffix=True)


def remove_prefix(subst, shl):
    return remove_affix(subst=subst, shl=shl, suffix=False)


def is_whitespace(s):
    return all(c in " \t\n" for c in s)


def follow_brace(shl, env, strict=False):
    """Expand and return expanded value up to the closing curly brace in
    ``shl``.
    """
    param = next(shl)
    logger_debug("follow_brace: param:", repr(param))
    if param == "#":
        word = next(shl)

        try:
            subst = env[word]
        except KeyError:
            if strict:
                raise ParameterExpansionNullError(word)
            else:
                subst = ""
        return str(len(subst))

    try:
        subst = env[param]
    except KeyError:
        if strict:
            raise ParameterExpansionNullError(param)
        else:
            subst = ""

    logger_debug("follow_brace: subst:", repr(subst))
    param_unset = param not in env
    param_set_and_not_null = bool(subst and (param in env))
    try:
        modifier = next(shl)
        logger_debug("follow_brace: modifier:", repr(modifier))
        if is_whitespace(modifier):
            pass
        elif modifier == "%":
            return remove_suffix(subst, shl)
        elif modifier == "#":
            return remove_prefix(subst, shl)
        elif modifier == ":":
            modifier = next(shl)
            if modifier == "-":
                word = next(shl)
                if param_set_and_not_null:
                    return subst
                return word
            elif modifier == "=":
                word = next(shl)
                if param_set_and_not_null:
                    return subst
                env[param] = word
                return word
            elif modifier == "?":
                if param_set_and_not_null:
                    return subst
                raise ParameterExpansionNullError(shl)
            elif modifier == "+":
                if param_set_and_not_null:
                    return next(shl)
                return subst  # ""
            elif modifier.isdigit() or modifier == ":":

                # This is a Substring Expansion as in ${foo:4:2}, ${foo::2},
                # ${foo:4:} or ${foo:4:2} in the generale form of
                # ${parameter:start:length}. No start means start=0. No length
                # means everything from start to end. This is a bash'ism, and
                # not POSIX.
                # see https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html

                logger_debug(f"    in substring: modifier1: {modifier}")

                if modifier == ":":
                    # if there is no start we have a slice that's {$foo::2}
                    start = 0
                    try:
                        length = int(next(shl))
                    except StopIteration:
                        # if there is no length we have a slice that's {$foo::}
                        # no slice in bash means length = 0
                        length = 0
                        return ""
                else:
                    try:
                        start = int(modifier)
                    except ValueError as e:
                        raise ParameterExpansionParseError(
                            "Not a bash substring", shl
                        ) from e

                    try:
                        modifier = next(shl)
                    except StopIteration:
                        # There is only a start and no length as in ${foo:4} and
                        # the length is therefore everything to the end i.e.
                        # with foo=123456 ${foo:4} is 56
                        if param_set_and_not_null:
                            return subst[start:]
                        else:
                            return subst

                    if modifier != ":":
                        raise ParameterExpansionParseError(
                            "Illegal substring argument", shl
                        )

                    try:
                        length = int(next(shl))
                    except StopIteration:
                        # If there is no length we have a substring that's
                        # {$foo::} no length in bash means length = 0
                        length = 0
                        return ""

                if param_set_and_not_null:
                    return subst[start : start + length]
                return subst
            else:
                raise ParameterExpansionParseError()

        elif modifier == "/":
            # This is a string replacement as in replace foo by bar using / as
            # sep.
            arg1 = next(shl)
            logger_debug("follow_brace: subst/1: arg1.1:", repr(arg1))
            replace_all = False
            if arg1 == "/":
                # with // replace all occurences
                replace_all = True
                arg1 = next(shl)

            has_sep = False

            # join anything in between the start / and middle /
            for na in shl:
                logger_debug("follow_brace: subst/1: shl/na:", repr(na))
                if na == "/":
                    has_sep = True
                    break
                arg1 += na

            logger_debug(
                "follow_brace: subst/1: arg1.2:", repr(arg1), "has_sep:", has_sep
            )

            arg2 = ""
            if has_sep:
                # Join anything in between the after the middle / until the end.
                # Note: the arg2 replacement value of a replacement may be empty
                for na in shl:
                    arg2 += na

            if param_set_and_not_null:
                if replace_all:
                    return subst.replace(arg1, arg2)
                else:
                    return subst.replace(arg1, arg2, 1)

            return subst

        else:
            if modifier == "-":
                word = next(shl)
                if param_unset:
                    return word
                return subst  # may be ""
            elif modifier == "=":
                word = next(shl)
                if param_unset:
                    env[param] = word
                    return word
                return subst  # may be ""
            elif modifier == "?":
                if param_unset:
                    msg = "".join(shl) or "parameter '$parameter' not found"
                    raise ParameterExpansionNullError(msg)
                return subst  # may be ""
            elif modifier == "+":
                word = next(shl)
                if param_unset:
                    return subst  # ""
                return word
            raise ParameterExpansionParseError()
    except StopIteration:
        return subst
