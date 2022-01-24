.. SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
..
.. SPDX-License-Identifier: CC-BY-4.0

Tests
=================================

Test fixture
----------------------------------------

Test fixtures are used by testcases in order to test a great amount of cases without writing a lot of code.

Documentation can be found at : https://docs.djangoproject.com/en/4.0/topics/testing/tools/#django.test.TransactionTestCase.fixtures

The test file must be under hermine/cube/fixtures/ and be named test_data.json.

In order to update the test fixxture (for example whenever there is a change in the model), you should run the following:

.. code-block:: shell

    manage.py cube dumpdata --indent=2 -e contenttypes -e auth.Permission > test_data.json

This excludes objects which are recreated automatically from schema every time during syncdb, and bring bugs.


API tests
----------------------------------------

.. automodule:: cube.tests.test_api_views
    :members:
