.. SPDX-FileCopyrightText: 2023 Henrik Sandklef
..
.. SPDX-License-Identifier: CC-BY-4.0


Background
==========

There are lots of software licenses out there (e.g. see `ScanCode
LicenseDB <https://scancode-licensedb.aboutcode.org/>`_), some of them
are FOSS and some not. In this project we primarily focus on FOSS licenses.

License name proliferation
--------------------------

When you're working with compliance you are used to liceses called
differently in source code or by tools (e.g. `GPLv2`, `GPL (v2)` and
`GNU General Public License Version 2`) when all you really want too
see is the `SPDX identifier <https://spdx.org/licenses/>`_ `GPL-2.0-only`. A seasoned compliance engineer or lawyer knows this already, but we need this information machine readable.

License proliferation
---------------------

Another problem you face when working with compliance is the need to
check whether the licenses in a combined work are compatible. One
example is the `X11-Style (Keith Packard)
<https://scancode-licensedb.aboutcode.org/x11-keith-packard.html>`_
license, which really is the same license as the `Historical
Permission Notice and Disclaimer - sell variant
<https://spdx.org/licenses/HPND-sell-variant.html>`_. `X11-Style
(Keith Packard)` is not supported in for example the `OSADL matrix <https://github.com/priv-kweihmann/osadl-matrix>`_, but `HPND-sell-variant` is. Again, a seasoned license engineer or lawyer knows which licenses are compatible and not, but we need to make it possible for a machine to assist us. 

Description
===========


FOSS Licenses
-------------

A database with meta data for FOSS licenses adding useful information
to existing licenses aiming at simplifying compliance work. The meta
data consists of:

* other names (aliases)

* compatibility as (another license)

* license text

Flame
-----

flame (FOSS License Additional MEtadata) provides:

* a Python API -  :ref:`python-api`

* command line tool -  :ref:`flame_Flame`

 
