# Matching Behavior

This page describes what happens to a license string before and during lookup.

## Quote Normalization

Before lookup, LicenseLynx normalizes recognized Unicode quote characters to the ASCII single quote `'`.

This helps when license strings are copied from PDFs, websites, office documents, or other sources that use typographic quotes.

Examples:

- `BSD ‚Zero‛ Clause` becomes `BSD 'Zero' Clause`
- `Licensed under the “MIT” license` becomes `Licensed under the 'MIT' license`

## Lookup Order

Lookup happens in this order:

1. Normalize quote characters.
2. Search the stable map.
3. If `risky` is enabled, search the risky map.
4. If `org` is provided, search the organization-specific map.

See [Risky Mappings](risky-mappings.md) for the meaning of the risky map.

## Recognized Quote Characters

All three libraries normalize the same set of characters:

```python
quote_characters = [
    # Single quotes
    "\u2018",  # LEFT SINGLE QUOTATION MARK '
    "\u2019",  # RIGHT SINGLE QUOTATION MARK '
    "\u201A",  # SINGLE LOW-9 QUOTATION MARK ‚
    "\u201B",  # SINGLE HIGH-REVERSED-9 QUOTATION MARK ‛
    "\u2032",  # PRIME (often used as an apostrophe) ′
    "\uFF07",  # FULLWIDTH APOSTROPHE ＇
    # Double quotes
    "\u201C",  # LEFT DOUBLE QUOTATION MARK "
    "\u201D",  # RIGHT DOUBLE QUOTATION MARK "
    "\u201E",  # DOUBLE LOW-9 QUOTATION MARK „
    "\u201F",  # DOUBLE HIGH-REVERSED-9 QUOTATION MARK ‟
    "\u2033",  # DOUBLE PRIME ″
    "\u00AB",  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK «
    "\u00BB",  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK »
    "\uFF02",  # FULLWIDTH QUOTATION MARK ＂
]
```

## Related Pages

- [Usage](../usage.md)
- [API Reference](../api-reference.md)
- [Risky Mappings](risky-mappings.md)
