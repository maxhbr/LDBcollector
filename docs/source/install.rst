.. SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
..
.. SPDX-License-Identifier: CC-BY-4.0

Install
==============


Install Poetry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is recommended to use Poetry to run Hermine.

See https://python-poetry.org/docs/ for full installation instructions.


Install Postgresql (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, Hermine uses SQLlite as database system.
You use a Postgres Database instead. If you do so, it is recommended by Django to set your user as it follows :

.. code-block::

    ALTER ROLE userName SET default_transaction_isolation TO ‘read committed’;
    ALTER ROLE userName SET timezone TO ‘UTC’;


Install Hermine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can clone the repository from GitLab either by SHH:

.. code-block:: bash

    git clone git@gitlab.com:hermine-project/hermine.git


Or by HTTPS:

.. code-block:: bash

    git clone https://gitlab.com/hermine-project/hermine.git


Go in the root folder and run

.. code-block:: bash

    poetry Install


This will install all the dependencies needed to run and develop Hermine. It should take less than 1 minute.

Now, you have to configure the connection to your database. To do so, create a mysecrets.py file:

.. code-block:: bash

    cd hermine/hermine/
    cp mysecrets.default.py mysecrets.py
    nano mysecrets.py

And change the mysecrets.py file to fit your database configuration.

If you've correctly configured your user with your database, you should be able to run the following:

.. code-block:: bash

    cd hermine
    python manage.py makemigrations # this generates, if needed, the django migration files to draw your database
    python manage.py migrate # Executes the SQL commands interpreted from migration files in the database
    python manage.py runserver 

That's it ! You have a working Hermine instance. Now, you can start from scratch or import data.

