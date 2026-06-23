# Risky Mappings

## The Problem

Some license strings are ambiguous. For example, `"gpl3"` clearly points at GPL 3, but does not say whether it means `GPL-3.0-only` or `GPL-3.0-or-later`. Mapping it by default would be a guess, which violates LicenseLynx's [data quality](data-quality.md) principle of deterministic mappings.

## How LicenseLynx Handles This

Instead of discarding ambiguous mappings entirely, LicenseLynx separates them into two tiers:

- **Stable map** (default) -- Only high-confidence, unambiguous mappings. This is what you get when you call `map()` without extra parameters.
- **Risky map** (opt-in) -- Plausible but uncertain mappings. Only searched when you explicitly enable it.

This way, the default behavior is always safe, but callers who prefer broader coverage over strict accuracy can opt in.
For the full lookup order, see [Matching Behavior](matching-behavior.md).

## When a Mapping Becomes Risky

A mapping is placed in the `risky` list of a license file when:

- The alias is ambiguous (could refer to multiple licenses)
- The alias lacks a version number where one is expected
- The mapping is based on common usage rather than an authoritative source
- The relationship between the alias and the canonical license is not fully verified

For family-specific conventions (for example the GNU `-or-later` default), see [Alias Decisions](alias-decisions.md).


## How to Enable

=== "Python"

    ```python
    from licenselynx.licenselynx import LicenseLynx

    # Stable only (default)
    result = LicenseLynx.map("gpl3")          # None

    # With risky mappings
    result = LicenseLynx.map("gpl3", risky=True)  # LicenseObject(id="GPL-3.0-or-later", src="spdx")
    ```

=== "Java"

    ```java
    import org.licenselynx.LicenseLynx;

    // Stable only (default)
    LicenseLynx.map("gpl3");          // null

    // With risky mappings
    LicenseLynx.map("gpl3", true);    // LicenseObject
    ```

=== "TypeScript"

    ```typescript
    import {map} from "@licenselynx/licenselynx";

    // Stable only (default)
    await map('gpl3');                // rejects

    // With risky mappings
    await map('gpl3', true);          // resolves to GPL-3.0-or-later
    ```

## Relationship to Rejected Mappings

Rejected mappings are different from risky ones. A **rejected** alias is one that was explicitly marked as *wrong* for a license -- it will never be returned, regardless of the `risky` flag. Risky mappings are *plausible but uncertain*; rejected mappings are *known to be incorrect*.

See the [Data Specification](data-specification.md) for the full field definitions.
