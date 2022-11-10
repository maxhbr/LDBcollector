# SPDX-License-Identifier: Apache-2.0
# Copyright (C) nexB Inc. and others
# Copyright (C) 2001-2020 NLTK Project
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/pygmars for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

"""

This module defines  ``Parser`` which is a regular expression-based parser to
parse list of Tokens in a parse tree where each node has a label.

This is originally based on NLTK POS chunk parsing used to identify non-
overlapping linguistic groups (such as base noun phrases) in unrestricted text.

This parsing can identify and group sequences of Tokens in a shallow parse Tree.
A parse Tree is a tree containing Tokens and Trees, where each sub-Tree contains
only Tokens.  For example, the parse Tree for base noun phrase groups in the
sentence "I saw the big dog on the hill" is::

  (SENTENCE:
    (NP: <I>)
    <saw>
    (NP: <the> <big> <dog>)
    <on>
    (NP: <the> <hill>))


Rule
======

``Rule`` uses regular-expressions over Token and Tree labels to parse and group
tokens and trees. The ``parse()`` method constructs a ``ParseString`` that
encodes a particular group of tokens.  Initially, nothing is grouped. ``Rule``
then applies its ``pattern`` substitution to the ``ParseString`` to modify the
token grouping that it encodes. Finally, the ``ParseString`` is transformed back
and returned as a parse Tree.

A ``Rule`` is used to parse a sequence of Tokens and assign a label to a sub-
sequence using a regular expression. Multiple ``Rule``s form a grammar used by a
``Parser``. Many ``Rule``s are typically loaded from a grammar text by a parser.


Rule pattern over labels
-------------------------

A ``pattern`` can update the grouping of tokens and trees by modifying a
``ParseString``. Each ``pattern`` ``apply_transform()`` method modifies the
grouping encoded by a ``ParseString``.

A ``pattern`` uses a modified version of regular expression patterns.  Patterns
are used to match sequence of Token or Tree labels. Examples of label patterns
are::

     r'(<DT>|<JJ>|<NN>)+'
     r'<NN>+'
     r'<NN.*>'

The differences between regular expression patterns and label patterns are:

    - In label patterns, ``'<'`` and ``'>'`` act as parentheses; so
      ``'<NN>+'`` matches one or more repetitions of ``'<NN>'``, not
      ``'<NN'`` followed by one or more repetitions of ``'>'``.

    - Whitespace in label patterns is ignored.  So
      ``'<DT> | <NN>'`` is equivalant to ``'<DT>|<NN>'``

    - In label patterns, ``'.'`` is equivalant to ``'[^{}<>]'``; so
      ``'<NN.*>'`` matches any single label starting with ``'NN'``.

The function ``label_pattern_to_regex`` is used to transform a label pattern to
an equivalent regular expression pattern which is then used internally over the
``ParseString`` encoding.

"""
# Originally based on: Natural Language Toolkit
# substantially modified for use in ScanCode-toolkit and a standalone library
#
# Natural Language Toolkit (NLTK)
# URL: <http://nltk.org/>
# Author: Edward Loper <edloper@gmail.com>
#         Steven Bird <stevenbird1@gmail.com> (minor additions)
#         Tiago Tresoldi <tresoldi@users.sf.net> (original affix tagger)
#
# The Natural Language Toolkit (NLTK) is an open source Python library
# for Natural Language Processing.  A free online book is available.
# (If you use the library for academic research, please cite the book.)
#
# Steven Bird, Ewan Klein, and Edward Loper (2009).
# Natural Language Processing with Python.  O'Reilly Media Inc.
# http://nltk.org/book

import re
from functools import partial

from pygmars import as_token_label
from pygmars.tree import Tree


class Parser:
    """
    Parser is a grammar-based parser that uses a grammar which is a list of Rule
    with patterns that are specialized regular expression for over Token or Tree
    labels. Internally the parsing of a Token and Tree sequence is encoded using
    a ``ParseString``, and each Rule pattern acts by modifying the grouping and
    parsing in the ``ParseString``. Rule patterns are implemented using regular
    expression substitution.

    The Rule patterns of a grammar are executed in sequence.  An earlier pattern
    may introduce a parse boundary that prevents a later pattern from matching.
    Sometimes an individual pattern will match on multiple, overlapping extents
    of the input.  As with regular expression substitution, the parser will
    identify the first match possible, then continue looking for all other
    following matches.

    The maximum depth of a parse tree created by a parser is the same as the
    number of Rules in the grammar.

    When tracing is turned on, the comment portion of a line is displayed each
    time the corresponding pattern is applied.
    """

    def __init__(self, grammar, root_label="ROOT", loop=1, trace=0, validate=False):
        """
        Create a new Parser from a ``grammar`` string and a ``root_label``.

        ``loop`` is the number of times to run through all the patterns (as the
        evaluation of Rules is sequential and     recursive).

        ``trace`` is the level of tracing to use when parsing a text.  ``0``
        will generate no tracing output; ``1`` will generate normal tracing
        output; and ``2`` or higher will generate verbose tracing output.

        If ``validate`` is True perform extra consistency checks and validation
        on rules and rule parse results.
        """
        self._grammar = grammar
        self.rules = list(Rule.from_grammar(grammar, root_label, validate=validate))
        self._root_label = root_label
        self._loop = loop
        self._trace = trace
        self._validate = validate

    def parse(self, tree):
        """
        Apply this parser to the ``tree`` parse Tree and return a parse Tree.
        The tree is modified in place and returned.
        """
        if not tree:
            raise Exception(f"Cannot parse empty tree: {tree!r}")

        trace = self._trace

        if not isinstance(tree, Tree):
            tree = Tree(self._root_label, tree)

        for i in range(self._loop):
            if trace:
                print(f'parse: loop# {i}')
            for parse_rule in self.rules:
                if trace:
                    print(f'parse: parse_rule: {parse_rule!r}')
                    print(f'parse: parse_tree len: {len(tree)}')
                tree = parse_rule.parse(tree=tree, trace=trace)
                if trace:
                    print(f'parse: parse_tree new len: {len(tree)}')
        return tree

    def __repr__(self):
        return f"<Parser with {len(self.rules)} rules>"

    def __str__(self):
        rules = "\n".join(map(str, self.rules))
        return f"<Parser with  {len(self.rules)} rules>\n{rules}"


class ParseString:
    """
    A ParseString is a string-based encoding of a particular parsing of a
    sequence of label from Tokens and Trees. This is used internally by the
    Parser. The ``ParseString`` class uses a backing string and a list:

    - a string of Token or Tree labels that encode the parsing of the input
    tokens. This is the string to which the Rule's pattern regular expression
    transformations are applied. This string contains a sequence of angle-
    bracket delimited labels (e.g. Token or Tree labels), with the grouping
    indicated by curly braces.  An example of this encoding is::

        {<DT><JJ><NN>}<VBN><IN>{<DT><NN>}{<DT><NN>}<VBD>

    - a parallel and backing list of Tokens and Trees called "pieces".

    ``ParseString`` are created from a Tree of Tokens and Trees or list of
    Tokens (built from lexed texts). Initially when starting from a list of
    Tokens, nothing is parsed and Tokens are not grouped in a Tree.

    The ``ParseString.apply_transform()`` method uses the Rule label pattern
    "transformer" to transform the backing string and mark which part of that
    string match the Rule pattern. This marking is then used to return a new
    parse Tree from the backing pieces.

    """
    # Anything that's not a delimiter such as <> or {}
    LABEL_CHARS = r"[^\{\}<>]"
    LABEL = fr"(<{LABEL_CHARS}+>)"

    # return a True'ish value if the parse results look valid
    is_valid = re.compile(r"^(\{?%s\}?)*?$" % LABEL).match

    def __init__(self, tree, validate=False):
        """
        Construct a new ``ParseString`` from a ``tree`` parse Tree of Tokens.
        """
        self._root_label = tree.label
        self._tree = tree
        self._parse_string = "".join(f"<{p.label}>" for p in tree)
        self._validate = validate

    def validate(self, s):
        """
        Validate that the string ``s`` corresponds to a parsed version of
        ``_tree``.

        Check individual tags and that the backing parse string encodes a parsed
        version of a list of tokens. And that the labels match those in
        ``_tree``.

        Raise ValueError if the internal string representation of this
        ``ParseString`` is invalid or not consistent with its _tree.
        """
        if not ParseString.is_valid(s):
            raise ValueError(f"Invalid parse:\n  {s}")

        if not has_balanced_non_nested_curly_braces(s):
            raise ValueError(f"Invalid parse: unbalanced or nested curly braces:\n  {s}")

        tags1 = tag_splitter(s)[1:-1]
        tags2 = [node.label for node in self._tree]
        if tags1 != tags2:
            raise ValueError(f"Invalid parse: tag changed:\n  {s}")

    def to_tree(self, label="GROUP", pieces_splitter=re.compile(r"[{}]").split):
        """
        Return a parse Tree for this ``ParseString`` using ``label`` as the root
        label. Raise a ValueError if a transformation creates an invalid
        ParseString.
        """
        if self._validate:
            self.validate(self._parse_string)

        tree = self._tree

        parse_tree = Tree(self._root_label, [])
        index = 0
        matched = False

        # Use this alternating splitter list to create the parse Tree.
        # We track if we have a match or not based on the curly braces.
        # The "pieces_splitter" will yield an alternation such that the first
        # item is not part of a match (and may be empty) and the next item is in
        # a match and the next not in a match and so on.
        # For instance:
        # >>> pieces_splitter("{<for>}<bar>")
        # ['',        '<for>', '<bar>']
        #  not match, match,   not match
        # >>> pieces_splitter("ads{<for>}{<bar>}")
        # ['ads',     '<for>', '',        '<bar>',  '']
        #  not match, match,   not match, match,    match
        for piece in pieces_splitter(self._parse_string):

            # Find the list of tokens contained in this piece.
            length = piece.count("<")
            subsequence = tree[index:index + length]

            # Add this list of tokens to our tree.
            if matched:
                parse_tree.append(Tree(label, subsequence))
            else:
                parse_tree.extend(subsequence)

            index += length
            matched = not matched

        return parse_tree

    def apply_transform(self, transformer):
        """
        Apply the given ``transformer`` callable transformation to the string
        encoding of this ``ParseString``.

        This transformation should only add and remove braces; it should *not*
        modify the sequence of angle-bracket delimited tags.  Furthermore, this
        transformation may not result in improper bracketing.  Note, in
        particular, that bracketing may not be nested.

        ``transformer`` is a callable that accepts a string and returns a
        string. Raise ValueError if this transformation generates an invalid
        ParseString.
        """
        # Do the actual substitution
        s = transformer(self._parse_string)

        # The substitution might have generated "empty groups"
        # (substrings of the form "{}").  Remove them, so they don't
        # interfere with other transformations.
        s = s.replace("{}", "")

        # Make sure that the transformation was legal.
        if self._validate:
            self.validate(s)

        # Save the transformation.
        self._parse_string = s
        return s

    def __repr__(self):
        return f"<ParseString: {self._parse_string!r}>"

    def __str__(self):
        """
        Return a formatted representation of this ``ParseString``. This
        representation includes extra spaces to ensure that labels will line up
        with the representation of other ``ParseString`` for the same text,
        regardless of the grouping.
        """
        # Add spaces to make everything line up.
        s = re.sub(r">(?!\})", r"> ", self._parse_string)
        s = re.sub(r"([^\{])<", r"\1 <", s)
        if s[0] == "<":
            s = " " + s
        return s.rstrip()


# used to split a ParseString on labels and braces delimiters
tag_splitter = re.compile(r"[\{\}<>]+").split

# return only {} curly brackets aka. braces
get_curly_braces = partial(re.compile(r"[^\{\}]+").sub, "")

# remove {4,} regex quantifiers
remove_quantifiers = partial(re.compile(r"\{\d+(?:,\d+)?\}").sub, "")


def has_balanced_non_nested_curly_braces(string):
    """
    Return True if ``string`` contains balanced and non-nested curly braces.

    Approach:
    - remove regex quantifiers
    - remove all non-braces characters
    - remove all balanced brace pairs.
    If there is nothing left, then braces are balanced and not nested.

    Balanced but nested:
    >>> "{{}}".replace("{}", "")
    '{}'

    Unbalanced:
    >>> "{{}{}".replace("{}", "")
    '{'
    >>> "{}{}}{}".replace("{}", "")
    '}'

    Balanced an not nested:
    >>> "{}{}{}".replace("{}", "")
    ''
    >>> remove_quantifiers("foo{4}")
    'foo'
    >>> remove_quantifiers("foo{}")
    'foo{}'
    >>> remove_quantifiers("foo{4}")
    'foo'
    >>> remove_quantifiers("foo{4,5}")
    'foo'

    >>> has_balanced_non_nested_curly_braces("{}{}{}")
    True
    >>> has_balanced_non_nested_curly_braces("{{}{}{}")
    False
    """
    cb = get_curly_braces(string)
    cb = remove_quantifiers(cb)
    return bool(not cb.replace("{}", ""))


# this should probably be made more strict than it is -- e.g., it
# currently accepts 'foo'.
is_label_pattern = re.compile(
    r"^((%s|<%s>)*)$" % (
        r"([^{}<>]|{\d+,?}|{\d*,\d+})+",
        r"[^{}<>]+"
    )
).match

remove_spaces = re.compile(r"\s").sub


def label_pattern_to_regex(label_pattern):
    """
    Return a regular expression pattern converted from ``label_pattern``.  A
    "label pattern" is a modified version of a regular expression, designed for
    matching sequences of labels.  The differences between regular expression
    patterns and tag patterns are:

    - In label patterns, ``'<'`` and ``'>'`` act as parentheses; so
      ``'<NN>+'`` matches one or more repetitions of ``'<NN>'``, not
      ``'<NN'`` followed by one or more repetitions of ``'>'``.

    - Whitespace in label patterns is ignored.  So
      ``'<DT> | <NN>'`` is equivalant to ``'<DT>|<NN>'``

    - In label patterns, ``'.'`` is equivalent to ``'[^{}<>]'``; so
      ``'<NN.*>'`` matches any single tag starting with ``'NN'``.

    In particular, ``label_pattern_to_regex`` performs the following
    transformations on the given pattern:

    - Replace '.' with '[^<>{}]'

    - Remove any whitespace

    - Add extra parens around '<' and '>', to make '<' and '>' act
      like parentheses, so that in '<NN>+', the '+' has scope
      over the entire '<NN>'; and so that in '<NN|IN>', the '|' has
      scope over 'NN' and 'IN', but not '<' or '>'.

    - Check to make sure the resulting pattern is valid.

    Raise ValueError if ``label_pattern`` is not a valid pattern. In particular,
    ``label_pattern`` should not include braces (except for quantifiers); and it
    should not contain nested or mismatched angle-brackets.
    """
    # Clean up the regular expression
    label_pattern = (
        remove_spaces("", label_pattern)
        .replace("<", "(?:<(?:")
        .replace(">", ")>)")
    )

    # Check the regular expression
    if not is_label_pattern(label_pattern):
        raise ValueError("Bad label pattern: %r" % label_pattern)

    return label_pattern.replace(".", ParseString.LABEL_CHARS)


class Rule:
    """
    A regular expression-based parsing ``Rule`` to find and label groups of
    labelled Tokens and Trees.  The grouping of the tokens is encoded using a
    ``ParseString``, and each rule acts by modifying the grouping in the
    ``ParseString`` with its ``pattern``.  The patterns are implemented using
    regular expression substitution.
    """

    def __init__(
        self,
        pattern,
        label,
        description=None,
        root_label="ROOT",
        validate=False,
    ):
        """
        Construct a new ``Rule`` from a ``pattern`` string for a ``label``
        string and an opetional ``description`` string.

        ``root_label`` is the label value used for the top/root node of the tree
        structure.
        """
        self.pattern = pattern
        self.label = label
        self.description = description
        self._root_label = root_label

        regexp = label_pattern_to_regex(pattern)
        regexp = fr"(?P<group>{regexp})"
        self._regexp = regexp
        # the replacement wraps matched tokens in curly braces
        self._repl = "{\\g<group>}"
        self._transformer = partial(re.compile(regexp).sub, self._repl)
        self._validate = validate
        if validate:
            self.validate()

    def validate(self):
        """
        Validate this Rule and raise Exceptions on errors.
        """
        if not self.pattern:
            raise Exception("Illegal Rule: empty pattern")

        if not self.label:
            raise Exception("Illegal Rule: empty label")

        if self.label != as_token_label(self.label):
            raise Exception(f"Illegal Rule label: {self.label}")

    def parse(self, tree, trace=0):
        """
        Parse the ``tree`` parse Tree and return a new parse Tree that encodes
        the parsing in groups of Token sequences.

        The set of nodes identified in the tree depends on the pattern of this
        ``Rule``.

        ``trace`` is the level of tracing when parsing.  ``0`` will generate no
        tracing output; ``1`` will generate normal tracing output; and ``2`` or
        higher will generate verbose tracing output.
        """
        if len(tree) == 0:
            raise Exception(f"Warning: parsing empty tree: {tree!r}")

        # the initial tree may be a list and not yet a tree
        try:
            tree.label
        except AttributeError:
            tree = Tree(self._root_label, tree)

        parse_string = ParseString(tree, validate=self._validate)

        before_parse = str(parse_string)
        if trace:
            print(f"Rule.parse transformer regex: {self._regexp}")

        parse_string.apply_transform(self._transformer)
        after_parse = str(parse_string)
        if after_parse != before_parse:
            # only update the tree and the trace if there have been changes from
            # this parse
            if trace:
                print()
                print("# Input parsed as label:", repr(self.label))
                if trace > 1:
                    # verbose
                    print(tree.pformat())
                    print(
                        "with pattern:",
                        self.description ,
                        "(" + repr(self.pattern) + ")"
                    )

                print("  before:", repr(before_parse))
                print("  after :", repr(after_parse))

            tree = parse_string.to_tree(self.label)
        return tree

    def __repr__(self):
        if self.description:
            return f"<Rule: {self.pattern} / {self.label} # {self.description}>"
        return f"<Rule: {self.pattern} / {self.label}>"

    __str__ = __repr__

    @classmethod
    def from_string(cls, string, root_label="ROOT", validate=False):
        """
        Create a Rule from a grammar rule ``string`` in this format::

          label: {pattern} # description

        Where ``pattern`` is a regular expression for the rule.  Any text
        following the comment marker (``#``) will be used as the rule's
        description:

        >>> from pygmars.parse import Rule
        >>> Rule.from_string('FOO: <DT>?<NN.*>+')
        <Rule: <DT>?<NN.*>+ / FOO>
        """
        label, _, pattern = string.partition(":")
        pattern, _, description = pattern.partition("#")
        label = label.strip()
        pattern = pattern.strip()
        description = description.strip()

        if not pattern:
            raise ValueError(f"Empty pattern: {string}")

        if not label:
            raise ValueError(f"Missing rule label: {string}")

        if pattern.startswith("{") and pattern.endswith("}"):
            pattern = pattern[1:-1]

        return Rule(
            pattern=pattern,
            label=label,
            description=description,
            root_label=root_label,
            validate=validate,
        )

    @classmethod
    def from_grammar(cls, grammar, root_label="ROOT", validate=False):
        """
        Yield Rules from ``grammar`` string. Raise Exceptions on errors.

        A grammar is a collection of Rules that can be built from a string. A
        grammar contains one or more rule (one rule per line) in this form::

         NP: <DT|JJ>          # determiners and adjectives

        Here NP is a label and "<DT|JJ>" is the pattern. The remainder after #
        is used as a description.
        """
        for line in grammar.splitlines(False):
            line = line.strip()
            if not line or line.startswith("#"):
                # Skip blank & comment-only lines
                continue
            yield cls.from_string(
                string=line,
                root_label=root_label,
                validate=validate,
            )
