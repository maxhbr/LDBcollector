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

print(license_object.id)
print(license_object.src)
```

## TypeScript

In TypeScript, you need to import the `map` function from the `LicenseLynx` module and use it to map a license name.

Example:

```typescript
import {map} from "@licenselynx/licenselynx";

// Map the license name
const licenseObject = map('license1');

console.log(licenseObject.id);
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
        System.out.println(licenseObject.getId());
        System.out.println(licenseObject.getSrc());
    }
}
```

## Data mapping

It is also possible to retrieve the whole license mapping as one json-file.
To always get the most recent version, use `/json/latest/mapping.json`.
