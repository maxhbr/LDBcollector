# LicenseLynx for TypeScript

In TypeScript, you need to import the ``map`` function from the ``LicenseLynx`` module and use it to map a license name.
The return value is an object with the canonical name and the source of the license.

## Installation

To install the library, run following command:

```shell
npm install @licenselynx/licenselynx
```

## Usage

```typescript
import {map} from "@licenselynx/licenselynx";

// Map the license name
const licenseObject = map('license1');
console.log(licenseObject.id);
console.log(licenseObject.src);

// Map the license name with risky mappings enabled
const licenseObject = map('license1', true);
```

## Organization Licenses

Organizations can register internal/proprietary license identifiers that are kept separate from OSS licenses.
To look up an organization license, pass the `org` parameter:

```typescript
import {map, Organization, isOrganizationSource, isOrganizationSourceOf} from "@licenselynx/licenselynx";

// Map a license name within an organization
const licenseObject = map('licenseName', false, Organization.Siemens);
```

Helper functions for inspecting organization sources:

```typescript
// Check if the license comes from any organization
isOrganizationSource(licenseObject); // returns true if from any org

// Check if the license comes from a specific organization
isOrganizationSourceOf(licenseObject, Organization.Siemens); // returns true if from Siemens
```

## License

This project is licensed under the [BSD 3-Clause "New" or "Revised" License](../LICENSE) (SPDX-License-Identifier: BSD-3-Clause).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
