# API Reference

## LicenseObject

The return type of `map()`. Holds the resolved canonical identifier and its source.

| Field | Type     | Description                                                                                  |
|-------|----------|----------------------------------------------------------------------------------------------|
| `id`  | `string` | Canonical license identifier (e.g., `"MIT"`, `"Apache-2.0"`, `"bsd-new"`)                    |
| `src` | `string` | Origin of the mapping: `"spdx"`, `"scancode-licensedb"`, `"custom"`, or an organization name |

=== "Python"

    ```python
    result.id   # str
    result.src  # str
    ```

=== "Java"

    ```java
    result.getId()   // String (annotated @Nonnull)
    result.getSrc()  // String (annotated @Nonnull, deprecated -- use getCanonicalSource())
    ```

=== "TypeScript"

    ```typescript
    result.id   // readonly string
    result.src  // readonly string
    ```

## map()

Maps a license name string to its canonical `LicenseObject`.

**Lookup order:**

1. Normalize Unicode quotes in the input to ASCII `'`
2. Search the **stable map** (high-confidence mappings)
3. If not found and `risky` is enabled, search the **risky map**
4. If not found and `org` is provided, search the organization-specific map

=== "Python"

    ```python
    LicenseLynx.map(
        license_name: str,
        risky: bool = False,
        org: Optional[Organization] = None
    ) -> Optional[LicenseObject]
    ```

    | Parameter | Type | Default | Description |
    |-----------|------|---------|-------------|
    | `license_name` | `str` | -- | License string to look up |
    | `risky` | `bool` | `False` | Include risky/ambiguous mappings in the search |
    | `org` | `Organization` | `None` | Additionally search organization-specific mappings |

    **Returns:** `LicenseObject` or `None` if no match is found.

    ```python
    from licenselynx.licenselynx import LicenseLynx
    from licenselynx.organization import Organization

    result = LicenseLynx.map("Apache-2.0")
    if result:
        print(result.id)   # "Apache-2.0"
        print(result.src)  # "spdx"

    # No match
    result = LicenseLynx.map("nonexistent")
    assert result is None

    # With risky mappings
    result = LicenseLynx.map("gpl3", risky=True)

    # With organization
    result = LicenseLynx.map("SISL-1.4", org=Organization.SIEMENS)
    ```

=== "Java"

    ```java
    static LicenseObject map(String licenseName)
    static LicenseObject map(String licenseName, boolean risky)
    static LicenseObject map(String licenseName, Organization organization)
    static LicenseObject map(String licenseName, boolean risky, Organization organization)
    ```

    | Parameter | Type | Default | Description |
    |-----------|------|---------|-------------|
    | `licenseName` | `String` | -- | License string to look up (annotated `@Nonnull`) |
    | `risky` | `boolean` | `false` | Include risky/ambiguous mappings in the search |
    | `organization` | `Organization` | `null` | Additionally search organization-specific mappings |

    **Returns:** `LicenseObject` or `null` (annotated `@CheckForNull`) if no match is found.

    ```java
    import org.licenselynx.LicenseLynx;
    import org.licenselynx.LicenseObject;
    import org.licenselynx.Organization;

    // Basic lookup
    LicenseObject result = LicenseLynx.map("Apache-2.0");
    if (result != null) {
        System.out.println(result.getId());   // "Apache-2.0"
        System.out.println(result.getSrc());  // "spdx"
    }

    // No match returns null
    LicenseObject missing = LicenseLynx.map("nonexistent");
    assert missing == null;

    // With risky mappings
    LicenseObject risky = LicenseLynx.map("gpl3", true);

    // With organization
    LicenseObject org = LicenseLynx.map("SISL-1.4", Organization.Siemens);

    // With both risky and organization
    LicenseObject both = LicenseLynx.map("SISL-1.4", true, Organization.Siemens);
    ```

=== "TypeScript"

    ```typescript
    map(licenseName: string, risky?: boolean, org?: Organization): Promise<LicenseObject>
    ```

    | Parameter | Type | Default | Description |
    |-----------|------|---------|-------------|
    | `licenseName` | `string` | -- | License string to look up |
    | `risky` | `boolean` | `false` | Include risky/ambiguous mappings in the search |
    | `org` | `Organization` | -- | Additionally search organization-specific mappings |

    **Returns:** `Promise<LicenseObject>`. Rejects with an `Error` if no match is found.

    ```typescript
    import {map, Organization} from "@licenselynx/licenselynx";

    // Basic lookup
    const result = await map('Apache-2.0');
    console.log(result.id);   // "Apache-2.0"
    console.log(result.src);  // "spdx"

    // With risky mappings
    const risky = await map('gpl3', true);

    // With organization
    const orgResult = await map('SISL-1.4', false, Organization.Siemens);

    // Error handling
    try {
        await map('nonexistent');
    } catch (e) {
        console.error(e.message);  // "License nonexistent not found."
    }
    ```

## Enums

### LicenseSource

Available in all three libraries.

=== "Python"

    ```python
    from licenselynx.license_source import LicenseSource

    LicenseSource.SPDX                # "spdx"
    LicenseSource.SCANCODE_LICENSEDB   # "scancode-licensedb"
    LicenseSource.CUSTOM               # "custom"
    ```

=== "Java"

    ```java
    import org.licenselynx.LicenseSource;

    LicenseSource.Spdx                // "spdx"
    LicenseSource.ScancodeLicensedb   // "scancode-licensedb"
    LicenseSource.Custom              // "custom"
    ```

=== "TypeScript"

    ```typescript
    import {LicenseSource} from "@licenselynx/licenselynx";

    LicenseSource.Spdx                // "spdx"
    LicenseSource.ScancodeLicensedb   // "scancode-licensedb"
    LicenseSource.Custom              // "custom"
    ```

### Organization

Used as the optional `org` parameter of `map()` to include organization-specific license mappings in the lookup.

=== "Python"

    ```python
    from licenselynx.organization import Organization

    Organization.SIEMENS   # "siemens"
    ```

=== "Java"

    ```java
    import org.licenselynx.Organization;

    Organization.Siemens   // "siemens"
    ```

=== "TypeScript"

    ```typescript
    import {Organization} from "@licenselynx/licenselynx";

    Organization.Siemens   // "siemens"
    ```

## Source Type Helpers

Methods to classify a `LicenseObject` by its source. All return `boolean`.

=== "Python"

    ```python
    from licenselynx.licenselynx import LicenseLynx
    from licenselynx.organization import Organization

    result = LicenseLynx.map("MIT")

    result.is_spdx_identifier()
    result.is_scancode_licensedb_identifier()
    result.is_custom_identifier()
    result.is_organization_source()
    result.is_organization_source_of(Organization.SIEMENS)
    ```

=== "Java"

    ```java
    import org.licenselynx.LicenseLynx;
    import org.licenselynx.LicenseObject;
    import org.licenselynx.Organization;

    LicenseObject result = LicenseLynx.map("MIT");

    result.isSpdxIdentifier();
    result.isScanCodeLicenseDbIdentifier();
    result.isCustomSource();
    result.isOrganizationSource();
    result.isOrganizationSource(Organization.Siemens);
    ```

=== "TypeScript"

    ```typescript
    import {
      isCustomIdentifier,
      isOrganizationSource,
      isOrganizationSourceOf,
      isScancodeLicensedbIdentifier,
      isSpdxIdentifier,
      map,
      Organization,
    } from "@licenselynx/licenselynx";

    const result = await map('MIT');

    isSpdxIdentifier(result);
    isScancodeLicensedbIdentifier(result);
    isCustomIdentifier(result);
    isOrganizationSource(result);
    isOrganizationSourceOf(result, Organization.Siemens);
    ```

## Quote Normalization

All libraries automatically normalize 14 Unicode quotation mark characters to ASCII `'` before lookup. This means license strings copied
from PDFs, Word documents, or web pages with typographic quotes will still match.

For the full list and examples, see [Matching Behavior](data/matching-behavior.md).
