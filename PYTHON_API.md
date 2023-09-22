<!--
SPDX-FileCopyrightText: 2023 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# flame - FOSS Licenses Python API 

# Installing: 

```shell
git clone git@github.com:hesa/foss-licenses.git
cd foss-licenses/python
pip install -r requirements.txt
python3 setup.py build sdist
pip install .
```

# Using

Create a LicenseDatabase object
```python
>>> from flame.license_db import FossLicenses
>>> fl = FossLicenses()

```

Get the license for "BSD3 & x11-keith-packard"
```python
>>> from flame.license_db import FossLicenses
>>> fl = FossLicenses()
>>> expression = fl.expression_license('BSD3 & x11-keith-packard')
>>> print(expression['identified_license'])
BSD-3-Clause AND LicenseRef-flame-x11-keith-packard

```

Get the compatible license expression for "BSD3 & x11-keith-packard"
```python
>>> from flame.license_db import FossLicenses
>>> fl = FossLicenses()
>>> expression = fl.expression_compatibility_as('BSD3 & x11-keith-packard')
>>> print(expression['compat_license'])
BSD-3-Clause AND HPND

```

