# LicenseLynx for TypeScript

In TypeScript, you need to import the ``map`` function from the ``LicenseLynx`` module and use it to map a license name.
The return value is an object with the canonical name and the source of the license.

## Installation

UNDER CONSTRUCTION

## Usage

```typescript
import {map} from 'LicenseLynx';

// Map the license name
const licenseObject = map('license1');
console.log(licenseObject.getCanonical());
console.log(licenseObject.getSrc());
```
