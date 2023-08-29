<!--
SPDX-FileCopyrightText: 2023 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# FOSS Licenses 

A database with meta data for FOSS licenses adding useful information to existing licenses aiming at simplifying compliance work. The meta data consists of:

* compatibility as (another license)

* other names (aliases)

* license text

# Database

The data can be found in the [var directory](https://github.com/hesa/foss-licenses/tree/main/var). Each license has a JSON file with meta information and a LICENSE file with the license text.

# Tools and APIs

* [flame](https://github.com/hesa/foss-licenses/blob/main/FLAME.md) - command line program

* [Python API](https://github.com/hesa/foss-licenses/blob/main/PYTHON_API.md) - well, a Python API

# Related tools and projects

* [flict](https://github.com/vinland-technology/flict) - FOSS License Compatibility Tool 

* [scancode](https://github.com/nexB/scancode-toolkit) - ScanCode toolkit

* [ScanCode LicenseDB](https://scancode-licensedb.aboutcode.org/) - a database with licenses

# Acknowledgements

* [Nexb](https://www.nexb.com/) for their general and generous work in FOSS compliance

* [Max Huber](https://github.com/maxhbr) for [LDBcollector](https://github.com/maxhbr/LDBcollector)

* [OSADL](https://www.osadl.org) for their [License Compatibility Matrix](https://www.osadl.org/Access-to-raw-data.oss-compliance-raw-data-access.0.html)