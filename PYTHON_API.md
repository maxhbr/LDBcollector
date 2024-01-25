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


## Extending flame

If you want to add your own licenses (e.g. your company's) you can do this in two different ways. But first we need to create a config file for that. Here are some assumptions:

* you define a license called `LicenseRef-mycompany-mylicense` having the same compatibility as `MIT` in a JSON file in `licenses` directory in the current folder, e.g. `./licenses/my-company-license.json`

* you define your flame config in a file, `flame-config.json`, in the current` directory: `./flame-config.json`


### Using the Python API

Here you don't need the config file and instead pass the directory in a config object directly to `FossLicenses`.

```python3
>>> from flame.license_db import FossLicenses
>>> fl = FossLicenses(config={'additional-license-dir': 'licenses'})
>>> expression = fl.expression_compatibility_as('LicenseRef-mycompany-mylicense')
>>> print(expression['compat_license'])
MIT

```
### Config file, environment variable and 

The config file, `flame-config.json`, looks like this:

```
{
    "additional-license-dir": "./licenses/"
}
```

Pass the config file using the environment varialbe `FLAME_USER_CONFIG`.

```FLAME_USER_CONFIG=flame-config.json python3
>>> from flame.license_db import FossLicenses
>>> fl = FossLicenses()
>>> expression = fl.expression_compatibility_as('LicenseRef-mycompany-mylicense')
>>> print(expression['compat_license'])
MIT

```

