# Usage

LicenseLynx provides libraries for Python, Java, and TypeScript, making it easy to integrate into projects regardless of the programming language.
Below are instructions and examples for each language.
In each language the method `map` returns an `LicenseObject`, which holds the information of the canonical name and source for the license name.

## Python

To use LicenseLynx in Python, you can call the `map` method from the `LicenseLynx` module to map a license name.

**Example:**

```python
from licenselynx.licenselynx import LicenseLynx

# Map the license name
license_object = LicenseLynx.map("licenseName")

print(license_object.canonical)
print(license_object.src)
```

## TypeScript

In TypeScript, you need to import the `map` function from the `LicenseLynx` module and use it to map a license name.

Example:

```typescript
import {map} from "@licenselynx/licenselynx";

// Map the license name
const licenseObject = map('license1');

console.log(licenseObject.canonical);
console.log(licenseObject.src);
```

## Java

For Java, use the `map` method from the `LicenseLynx` class to achieve the same functionality.

Example:

```java
import org.licenselynx.*;

public class LicenseExample {
    public static void main(String[] args) {
        // Map the license name
        LicenseObject licenseObject = LicenseLynx.map("licenseName");

        System.out.println(licenseObject.canonical);
        System.out.println(licenseObject.src);
    }
}
```

## Web API

The LicenseLynx Web API simulates an API environment but functions as a file directory hosted on GitLab Pages.
To maintain compatibility with this structure, any entry containing a / must be replaced with an _.
Below are the instructions for making this replacement in both Windows and Linux systems for bash and powershell if the modification should be done programmatically.

The API call format is: `/api/license/{license_name}.json`

Because the Web API is a file directory, the extension `.json` must be added to find the file. Also, the characater ``/`` must be replaced with ``_``.

**Example API Call**:

Original License Name:

```bash
Apache-2.0/License
```

Formatted license name for API Call:

```bash
Apache-2.0_License
```

API Call:

```bash
/api/license/Apache-2.0_License.json
```

## Data mapping

It is also possible to retrieve the whole license mapping as one json-file.
To always get the most recent version, use `/json/latest/mapping.json`.
