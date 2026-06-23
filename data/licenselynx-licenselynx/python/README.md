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

print(license_object.id)
print(license_object.src)

# Map the license name with risky mappings enabled
license_object = LicenseLynx.map("licenseName", risky=True)

```

## Organization Licenses

Organizations can register internal/proprietary license identifiers that are kept separate from OSS licenses.
To look up an organization license, pass the `org` parameter:

```python
from licenselynx.licenselynx import LicenseLynx
from licenselynx import Organization

# Map a license name within an organization
license_object = LicenseLynx.map("licenseName", org=Organization.SIEMENS)
```

The `LicenseSource` enum is also available for inspecting the source type:

```python
from licenselynx import LicenseSource
```

Helper methods on the returned license object:

```python
# Check if the license comes from any organization
license_object.is_organization_source()  # returns True if from any org

# Check if the license comes from a specific organization
license_object.is_organization_source_of(Organization.SIEMENS)  # returns True if from Siemens
```

## License

This project is licensed under the [BSD 3-Clause "New" or "Revised" License](../LICENSE) (SPDX-License-Identifier: BSD-3-Clause).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
