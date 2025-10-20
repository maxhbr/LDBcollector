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
console.log(licenseObject.canonical);
console.log(licenseObject.src);

// Map the license name with risky mappings enabled
const licenseObject = map('license1', true);
```

## License

This project is licensed under the [BSD 3-Clause "New" or "Revised" License](../LICENSE) (SPDX-License-Identifier: BSD-3-Clause).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
