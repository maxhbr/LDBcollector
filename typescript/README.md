# License Lynx for TypeScript

In TypeScript, you need to import the ``map`` function from the ``LicenseLynx`` module and use it to map a license name.

## Usage

```typescript
import { map } from 'LicenseLynx';

// Map the license name
const canonicalName = map('license1');
console.log(canonicalName);
```