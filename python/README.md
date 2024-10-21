# LicenseLynx for Python

To use LicenseLynx in Python, you can call the ``map`` method from the ``LicenseLynx`` module to map a license name to its canonical form.
The return value is an object with the canonical name and the source of the license.

## Usage

```python
from licenselynx.licenselynx import LicenseLynx

# Map the license name
license_object = LicenseLynx.map("licenseName")

print(license_object.canonical)
print(license_object.src)
```
