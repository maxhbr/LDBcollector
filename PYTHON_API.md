<!--
SPDX-FileCopyrightText: 2023 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# flame - FOSS Licenses Python API 

# Installing: 

```
git clone git@github.com:hesa/foss-licenses.git
cd foss-licenses/python
pip install -r requirements.txt
pip install .
```

# Using

Create a LicenseDatabase object
```
from flame.license_db import LicenseDatabase
ldb = LicenseDatabase()
```

Get the alias for "BSD3 & x11-keith-packard"
```
from flame.license_db import LicenseDatabase
ldb = LicenseDatabase()
expression = ldb.expression('BSD3 & x11-keith-packard')
print(expression['identified_license'])
```

Get the compatible license expression for "BSD3 & x11-keith-packard"
```
from flame.license_db import LicenseDatabase
ldb = LicenseDatabase()
expression = ldb.expression_compatibility_as('BSD3 & x11-keith-packard')
print(print(expression['compat_license']))
```


