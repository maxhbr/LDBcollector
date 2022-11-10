# SPDX-License-Identifier: Apache-2.0
# Copyright (C) nexB Inc. and others
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/pygmars for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import re
from collections import namedtuple


class Token:
    """
    Represent a word token with its label, line number and line position.
    """
    #  keep memory requirements low by preventing creation of instance dicts.
    __slots__ = (
        # the string value of a token
        'value',
        # a token label as a string.
        # this is converted to an UPPER-CASE, dash-seprated string on creation
        'label',
        # starting line number in the original text, one-based
        'start_line',
        # the positition of this token; typically a token pos in its line, zero-
        # based, but can be an absolute position or an offset too
        'pos',
    )

    def __init__(self, value, label=None, start_line=None, pos=None):
        self.value = value
        self.label = as_token_label(label) if label else None
        self.start_line = start_line
        self.pos = pos

    def __repr__(self, *args, **kwargs):
        return f'(label={self.label!r}, value={self.value!r})'

    def __str__(self, *args, **kwargs):
        return f'Token(value={self.value!r}, label={self.label!r}, start_line={self.start_line}, pos={self.pos})'

    @classmethod
    def from_numbered_lines(cls, numbered_lines, splitter=str.split):
        """
        Return an iterable of tokens built from a ``numbered_lines`` iterable of
        tuples of (line number, text). Use the ``splitter`` callable to split
        a line in words/tokens. The line numbers are expected to be one-based.
        """
        for start_line, line in numbered_lines:
            for line_pos, value in enumerate(splitter(line)):
                yield cls(value, label=None, start_line=start_line, pos=line_pos)

    @classmethod
    def from_lines(cls, lines, splitter=str.split):
        """
        Return an iterable of tokens built from a ``lines`` iterable of strings
        Use the ``splitter`` callable to split a line in words/tokens.
        The line numbers are one-based.
        """
        numbered_lines = enumerate(lines, 1)
        return cls.from_numbered_lines(numbered_lines, splitter)

    @classmethod
    def from_string(cls, s, splitter=str.split):
        """
        Return an iterable of tokens built from a ``s`` string. Use the
        ``splitter`` callable to split a line in words/tokens. The line numbers
        are one-based.
        """
        lines = s.splitlines(False)
        numbered_lines = enumerate(lines, 1)
        return cls.from_numbered_lines(numbered_lines, splitter)

    @classmethod
    def from_value_label_tuples(cls, value_labels):
        """
        Return an iterable of tokens built from a ``value_labels`` iterable of
        tuples of token (value, label).
        """
        for pos, (value, label) in enumerate(value_labels):
            yield cls(value, label=label, pos=pos)

    @classmethod
    def from_pygments_tokens(cls, pygtokens):
        """
        Return an iterable of Tokens built from a ``pygtokens`` iterable of
        tuples (pos, Pygments token, string value) as produced by Pygments
        lexers. The Pygments Token types are normalized to a Token.label, all
        uppercase and dash-separated. The pygmars.Token.label is derived from
        the qualified class name of the Pygments pygments.token.Token class
        name, ignoring the first "Token." segment which is consistent with
        Pygments handling. The pygments.token._TokenType for Tokens is peculiar
        as it overrides __getattr__ to create new Token types.
        """
        lineno = 1
        for pos, tokentype, value in pygtokens:
            label = convert_pygments_token_to_label(tokentype)
            yield cls(value, label=label, pos=pos, start_line=lineno)
            lineno += value.count('\n')


def convert_pygments_token_to_label(token):
    """
    Return a string suitabel to use as a pygmars.Token.label given a Pygments
    ``token`` pygments.token.Token-like object.

    For example, let's create a Pygments-like ojects:
    >>> convert_pygments_token_to_label('Token.Text')
    'TEXT'
    >>> convert_pygments_token_to_label('Token.Text.Whitespace')
    'TEXT-WHITESPACE'
    >>> convert_pygments_token_to_label('Token')
    'TOKEN'
    """
    # take the string of the pygments type, as in "Token.Text.Whitespace"
    label = str(token)
    # strip leading "Token." dotted segment, unless that's the only segment to get as in "Text.Whitespace"
    if label != 'Token' and '.' in label:
        _stripped, _, label = label.partition('.')
    # normalize to "TEXT-WHITESPACE"
    label = as_token_label(label)
    return label


only_wordchars = re.compile(r'[^A-Z0-9\-]').sub


def as_token_label(s):
    """
    Return a string derived from `s` for use as a token label. Token labels are
    strings made only of uppercase ASCII letters, digits and dash separators.
    They do not start with a digit or dash and do not end with a dash.
    """
    s = str(s).upper()
    s = only_wordchars(' ', s)
    s = ' '.join(s.split())
    s = s.replace(' ', '-').replace('--', '-').strip('-').lstrip('0123456789')
    return s
