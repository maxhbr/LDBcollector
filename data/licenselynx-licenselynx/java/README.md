# LicenseLynx for Java

Use the `map` method from the `LicenseLynx` class to get a `LicenseObject` to access license properties.

## Installation

To install the Java library, add it to your [Gradle](https://gradle.org/) or [Maven](https://maven.apache.org/) build.

Gradle `build.gradle`:

```groovy
implementation 'org.licenselynx:licenselynx:2.2.0'
```

Gradle `build.gradle.kts`:

```kotlin
implementation("org.licenselynx:licenselynx:2.2.0")
```

Maven `pom.xml`:

```xml

<dependency>
    <groupId>org.licenselynx</groupId>
    <artifactId>licenselynx</artifactId>
    <version>2.2.0</version>
</dependency>
```

## Usage

```java
import org.licenselynx.*;

public class LicenseExample {
    public static void main(String[] args) {
        // Map the license name
        LicenseObject licenseObject = LicenseLynx.map("licenseName");
        System.out.println(licenseObject.getId());
        System.out.println(licenseObject.getSrc());
        
        // Map the license name with risky mappings enables
        LicenseObject licenseObject = LicenseLynx.map("licenseName", true);
    }
}
```

## Organization Licenses

Organizations can register internal/proprietary license identifiers that are kept separate from OSS licenses.
The `Organization` enum is available from `org.licenselynx.*`.

```java
import org.licenselynx.*;

// Map a license name within an organization
LicenseObject licenseObject = LicenseLynx.map("licenseName", Organization.Siemens);

// Map with risky mappings enabled and an organization
LicenseObject licenseObject = LicenseLynx.map("licenseName", true, Organization.Siemens);
```

Helper methods on `LicenseObject`:

```java
// Check if the license comes from any organization
licenseObject.isOrganizationSource(); // returns true if from any org

// Check if the license comes from a specific organization
licenseObject.isOrganizationSource(Organization.Siemens); // returns true if from Siemens

// Get the canonical source (preferred over getSrc() and getLicenseSource())
CanonicalSource source = licenseObject.getCanonicalSource();
```

> **Note:** `getSrc()` and `getLicenseSource()` are deprecated in favor of `getCanonicalSource()`.

## License

This project is licensed under the [BSD 3-Clause "New" or "Revised" License](../LICENSE) (SPDX-License-Identifier:
BSD-3-Clause).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
