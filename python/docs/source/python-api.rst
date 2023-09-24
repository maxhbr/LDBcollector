.. SPDX-FileCopyrightText: 2023 Henrik Sandklef
..
.. SPDX-License-Identifier: CC-BY-4.0


.. _python-api:

Using the Python API
====================

FOSSLicenses
------------


Creating A FossLicenses object
..............................

Creating a FossLicenses object gives you an easy to use access to the
license database provided by FossLicenses. 

.. autofunction:: flame.license_db.FossLicenses

FossLicenses methods
....................

.. autofunction:: flame.license_db.FossLicenses.expression_license

.. autofunction:: flame.license_db.FossLicenses.alias_list
                  
.. autofunction:: flame.license_db.FossLicenses.license

.. autofunction:: flame.license_db.FossLicenses.license_complete

.. autofunction:: flame.license_db.FossLicenses.licenses

.. autofunction:: flame.license_db.FossLicenses.expression_compatibility_as

.. autofunction:: flame.license_db.FossLicenses.compatibility_as_list
                  
.. autofunction:: flame.license_db.FossLicenses.operators


Formatters
----------

Creating a Formatter
....................

.. autofunction:: flame.format.OutputFormatterFactory.formatter

Formatter methods
.................

.. .. autofunction:: flame.format.OutputFormatter

.. autofunction:: flame.format.OutputFormatter.format_compat

.. autofunction:: flame.format.OutputFormatter.format_compat_list

.. autofunction:: flame.format.OutputFormatter.format_alias_list


.. autofunction:: flame.format.OutputFormatter.format_expression
                  
.. autofunction:: flame.format.OutputFormatter.format_error
   
.. autofunction:: flame.format.OutputFormatter.format_licenses
   
.. autofunction:: flame.format.OutputFormatter.format_license_complete
   
.. autofunction:: flame.format.OutputFormatter.format_compatibilities
   
.. autofunction:: flame.format.OutputFormatter.format_operators
