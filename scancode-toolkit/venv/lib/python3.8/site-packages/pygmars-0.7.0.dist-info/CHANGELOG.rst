================
Changelog
================



Version 0.7.0
-----------------

- Improve tracing: it is now possible to trace lexing. Tracing parsing
  only reports which parsing actually was applied (rather than listing all)

- Enable custom regex re flags in Lexer.

- Convert generators to list when building a Tree.

- When using Pygments lexers, the token label crafted from a Pygments token
  type is stripped from the leading "Token."

- Improve Tree representation to make it easier to read traces


Version 0.6.0
---------------

- Use raw strings for regexes to avoid deprecation warnings

- Significantly refactor code: top level are lex, parse and tree

- Parsing is now restructured with only Parser and Rule, plus ParseString
  used internally for parsing.

- Code has been streamlined and simplified removing all parts that are not used
  As an unintended side effect, parsing is now roughly twice faster.
  For instance the scancode copyright test suite runs now in ~70 sec and was
  running in ~160 sec before this.

- Lexer now accepts callables that behave like re.match in addition to regexp

- Add minimal support to reuse Pygments lexer outputs and convert to Tokens to
  feed a Parser. This allow to build simple grammar-driven parser from Pygments
  lexers


Version 0.5.0
---------------

- Initial version derived from NLTK HEAD at a5690ee
