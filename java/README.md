# LicenseLynx for Java

Use the `map` method from the `LicenseLynx` class to get a `LicenseObject` to access license properties.

## Installation

To install the Java library, add it to your [Gradle](https://gradle.org/) or [Maven](https://maven.apache.org/) build.

Gradle `build.gradle`:

```groovy
implementation 'org.licenselynx:licenselynx:1.0.0'
```

Gradle `build.gradle.kts`:

```kotlin
implementation("org.licenselynx:licenselynx:1.0.0")
```

Maven `pom.xml`:

```xml
<dependency>
    <groupId>org.licenselynx</groupId>
    <artifactId>licenselynx</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Usage

```java
import org.licenselynx.*;

public class LicenseExample {
    public static void main(String[] args) {
        // Map the license name
        LicenseObject licenseObject = LicenseLynx.map("licenseName");
        System.out.println(licenseObject.getCanonical());
        System.out.println(licenseObject.getSrc());
        
        // Map the license name with risky mappings enables
        LicenseObject licenseObject = LicenseLynx.map("licenseName", true);
    }
}
```

## License

This project is licensed under the [Apache License, Version 2.0](../LICENSE.md) (SPDX-License-Identifier: Apache-2.0).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
