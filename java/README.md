# LicenseLynx for Java

For Java, use the ``map`` method from the ``LicenseLynx`` class to achieve the same functionality.

## Installation

To install the Java library, add it to Gradle or Maven build.

build.gradle:

```groovy
implementation 'org.licenselynx:licenselynx:1.0.0'
```

pom.xml:

```xml

<dependency>
    <groupId>org.licenselynx</groupId>
    <artifactId>licenselynx</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Usage

```java
import com.siemens.licenselynx.*;

public class LicenseExample {
    public static void main(String[] args) {
        // Map the license name
        LicenseObject licenseObject = LicenseLynx.map("licenseName");
        System.out.println(licenseObject.getCanonical());
        System.out.println(licenseObject.getSrc());
    }
}
```

## License

This project is licensed under the [Apache License, Version 2.0](../LICENSE.md) (SPDX-License-Identifier: Apache-2.0).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
