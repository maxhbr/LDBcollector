<!--
SPDX-FileCopyrightText: 2024 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# FOSS Licenses 

A database with meta data for FOSS licenses adding useful information to existing licenses aiming at simplifying compliance work. The meta data consists of:

* other names or aliases for licenses (e.g. "GNU GPL v. 2" is replaced by "GPL-2.0-only")

* fixes for compound license written as one single license or using faulty syntax (e.g. "GPL-2.0-with-classpath-exception" -> "GPL-2.0-only WITH Classpath-exception-2.0")

* other names for operators (e.g. "||" is replaced by "OR")

* translation of license with dual license features to a compound license expression (e.g. "GPL-2.0-or-later" -> "GPL-2.0-only OR GPL-3.0-only")

* compatibility as another license (e.g. "X11-Style (Keith Packard)" is compatibility wise the same as "HPND")

* ambiguous license name (e.g. "GNU General Public License", which misses the version number)

* license text

# Background

There are lots of software licenses out there (e.g. see [ScanCode LicenseDB](https://scancode-licensedb.aboutcode.org/)), some of them are FOSS and some not. In this project we primarily focus on FOSS licenses.

## License name proliferation

When you're working with compliance you are used to liceses called differently in source code or by tools (e.g. `GPLv2`, `GPL (v2)` and `GNU General Public License Version 2`) when all you really want too see is the [SPDX identifier](https://spdx.org/licenses/) `GPL-2.0-only`. A seasoned compliance engineer or lawyer knows this already, but we need this information machine readable.

## License proliferation

Another problem you face when working with compliance is the need to check whether the licenses in a combined work are compatible. One example is the [`X11-Style (Keith Packard)`](https://scancode-licensedb.aboutcode.org/x11-keith-packard.html) license, which really is the same license as the [Historical Permission Notice and Disclaimer - sell variant](https://spdx.org/licenses/HPND-sell-variant.html). `X11-Style (Keith Packard)` is not supported in for example the OSADL matrix, but `HPND-sell-variant` is. Again, a seasoned license engineer or lawyer knows which licenses are compatible and not, but we need to make it possible for a machine to assist us. 

# About

This projet aims at providing a database with:

* "all" different names for a license in a database

* mappings from one license to another license which is supported by the OSADL matrix

and, to make the database easier to use:

* a Python API

* command line tool

# Database

The data can be found in the [var directory](https://github.com/hesa/foss-licenses/tree/main/var). Each license has a JSON file with meta information and a LICENSE file with the license text.

# Tools and APIs

* [flame](https://github.com/hesa/foss-licenses/blob/main/FLAME.md) - command line program

* [Python API](https://github.com/hesa/foss-licenses/blob/main/PYTHON_API.md)

# Contributions

You are more than welcome to contribute.

## License reviews

It would be great if you could check the licenses and feedback us (see HOW below). 

## Hacking

If you find a bug and have a fix or have written a new feature you want addded. Create a PR and we'll have a look..

## Suggest new features and report bugs

We need input from you on how you use or would like to use foss-licenses. 

## Suggest new license to support

Do you miss a license that you want support for. Create an issue with the following information:

* SPDX identifier (if any)

* Scancode identifier (if any)

* License text (or a URL)

* Aliases you would like to add (if any)

* Same compatibility as another license (if any)

## How

* create an [issue](https://github.com/hesa/foss-licenses/issues)

* create PR for code or license contributions

## CLA?

We do not have a CLA or similar, but we assume your contributions are
made under our license (for the code and data).

# Related tools and projects

* [flict](https://github.com/vinland-technology/flict) - FOSS License Compatibility Tool 

* [License Compatibility Matrix](https://www.osadl.org/Access-to-raw-data.oss-compliance-raw-data-access.0.html) - a matrix with license compatibilities

* [scancode](https://github.com/nexB/scancode-toolkit) - ScanCode toolkit

* [ScanCode LicenseDB](https://scancode-licensedb.aboutcode.org/) - a database with licenses

# Acknowledgements

* [Nexb](https://www.nexb.com/) for their FOSS compliance tools, especially [scancode](https://github.com/nexB/scancode-toolkit) and [ScanCode LicenseDB](https://scancode-licensedb.aboutcode.org/).

* [Max Huber](https://github.com/maxhbr) for [LDBcollector](https://github.com/maxhbr/LDBcollector)

* [OSADL](https://www.osadl.org) for their [License Compatibility Matrix](https://www.osadl.org/Access-to-raw-data.oss-compliance-raw-data-access.0.html)

# Technical notes

## Normalizing license expressions

We fix your license expressions with the following methods (listed in order)

### Normalize aliases

With our database we can replace a license like "GPLv2+" to the SPDX
identifier "GPL-2.0-or-later". We do this by searching for needles and
replace them. To search for needles, in our case license expressions,
(e.g. "BSD 0-Clause") to replace (with e.g. "0BSD") we use the
following strategy:

* list all needles in order of length, longest first

* for each needle find and replace

This is a naive approach but given the limited data at hand it should work.

### Normalize compound license expressions

Some compound licenses (e.g. "GPL-2.0-only WITH
Classpath-exception-2.0") are stated incorrectly (e.g. "GPL-2.0-only
AND Classpath-exception-2.0") or as a singe license
(""GPL-2.0-with-classpath-exception). The license expression is
scanned for licenses as listed in `var/compounds.json` and replaced
accordingly.

## Normalize operators

The license expression is scanned for operators as listed in
`var/operators.json` and replaced accordingly (e.g. "||" is replaced
by "OR").

## Normalize dual licenses

Some licenses have a built in dual license feature
(e.g. "GPL-2.0-or-later"). We replace such licenses with the
corresponding dual licenses.

As an example: "GPL-2.0-or-later" is replacde by "(GPL-2.0-only OR GPL-3.0-only")

## Insert same compatibility as another license

Some licenses are not supported by the OSADL license matrix (e.g.
"X11-Style (Keith Packard)") but the license is very similar and has
the same compatibility towards other licenses as another license
(e.g. "HPND").

To allow for tools (e.g. flict) to check compatibility of an inbound
license expression against an outbound license expression we replace
the unknown license with the known and with same compatibility.


# Extending flame

## Python API

See [Python API](https://github.com/hesa/foss-licenses/blob/main/PYTHON_API.md)

## Command line program

You can extend [flame](https://github.com/hesa/foss-licenses/blob/main/FLAME.md), the command line program, in two different ways:

* using the option `additional-license-dir`

* using the environment variable `FLAME_USER_CONFIG`

### Using the option `additional-license-dir`

Assuming you want to extend flame with the licenses located in the directory `more-licenses` and then list the licenses (using the command `licenses`):

```
flame --additional-license-dir more-licenses licenses
```

### Using the environment variable `FLAME_USER_CONFIG`

You have a config file, called `flame-config.json`, with the variable `additional-license-dir`set to `more-licenses`, like this:

```
{
    "additional-license-dir": "./more-licenses/"
}
```

then you can start `flame` to read the config file like this:

```
FLAME_USER_CONFIG=flame-config.json flame licenses
```
