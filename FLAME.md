<!--
SPDX-FileCopyrightText: 2023 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# flame (FOSS License Additional MEtadata)

# Installing: 

```
git clone git@github.com:hesa/foss-licenses.git
cd foss-licenses/python
pip install -r requirements.txt
pip install .
```

# Using

## Help 

```
$ flame --help
```

```
$ flame expressions --help
```

## Get spdx identifier(s) for a license expression

You want to know the license for `BSD3`
```
$ flame expression BSD3
BSD-3-Clause
```

You want to know the license for `BSD3 & x11-keith-packard`
```
$ flame expression "BSD3 & x11-keith-packard"
BSD-3-Clause AND LicenseRef-flame-x11-keith-packard
```

You want to know the license for `BSD3 & x11-keith-packard` and how the data was found
```
$ flame --verbose expression "BSD3 & x11-keith-packard"
BSD-3-Clause AND LicenseRef-flame-x11-keith-packard
 * "BSD3" -> "BSD-3-Clause via "alias"
 * "&" -> "AND via "operator"
 * "x11-keith-packard" -> "LicenseRef-flame-x11-keith-packard via "scancode_key"
```


## Get a license expression with compatible licenses

You want an expression with licenses that are supported by [osadl_matrix](https://github.com/priv-kweihmann/osadl-matrix):
```
$ flame compat "BSD3 & x11-keith-packard"
BSD-3-Clause AND HPND
```

You want an expression with licenses that are supported by [osadl_matrix](https://github.com/priv-kweihmann/osadl-matrix) from `BBSD3 & x11-keith-packard` with info on how the data was found:
```
$ flame --verbose compat "BSD3 & x11-keith-packard"
BSD-3-Clause AND HPND
 * "BSD3" -> "BSD-3-Clause" via "alias" -> "BSD-3-Clause" via "direct"
 * "&" -> "AND" via "operator"
 * "x11-keith-packard" -> "LicenseRef-flame-x11-keith-packard" via "scancode_key" -> "HPND" via "compatibility_as"
```

## List aliases

To list all the supported aliases (incomplete listing below):
``` 
$ flame aliases
GPL-2.0-only -> GPL-2.0-only
GPL-2.0 -> GPL-2.0-only
GPL2.0 -> GPL-2.0-only
GPL2 -> GPL-2.0-only
....
``` 

## List licenses

To list all the supported licenses (incomplete listing below):
``` 
$ flame licenses
BSD-3-Clause
GPL-2.0-only
....
``` 

## List operators

To list all the supported operators (incomplete listing below):
``` 
$ flame operators
OR -> OR
or -> OR
....
``` 

## Compatibilities

To list all licenses that has a license with same compatibility as an license known to [osadl_matrix](https://github.com/priv-kweihmann/osadl-matrix) (incomplete listing below):
``` 
$ flame compats
LicenseRef-flame-x11-keith-packard -> HPND
....
``` 

## Format

The following output formats are supported:

* JSON - e.g. `flame -of json expression BSD3`

* Yaml - e.g. `flame -of yaml expression BSD3`

* text - e.g. `flame -of text expression BSD3` (default format)
