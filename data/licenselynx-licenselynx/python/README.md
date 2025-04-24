# LicenseLynx for Python

To use LicenseLynx in Python, you can call the ``map`` method from the ``LicenseLynx`` module to map a license name to its canonical form.
The return value is an object with the canonical name and the source of the license.

## Installation

To install the library, run following command:

```shell
pip install licenselynx 
```

## Usage

```python
from licenselynx.licenselynx import LicenseLynx

# Map the license name
license_object = LicenseLynx.map("licenseName")

print(license_object.canonical)
print(license_object.src)
```

## License

This project is licensed under the [Apache License, Version 2.0](../LICENSE.md) (SPDX-License-Identifier: Apache-2.0).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
