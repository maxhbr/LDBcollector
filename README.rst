OSCAd: Open Source Compliance Advisor
=====================================

OSCAd is written in the Python programming language and uses the `Pyramid Web
Framework <http://docs.pylonsproject.org/projects/pyramid/en/latest/index.htmlhttp://docs.pylonsproject.org/projects/pyramid/en/latest/index.html>`_
and `Jinja2 Engine <http://jinja.pocoo.org/>`_ for templating.
Translations are based on gettext message catalogs. Translations in the
templates are done with the in the templates integrated i18n facilities.
In normal Python code `translationstring <http://docs.pylonsproject.org/projects/translationstring/en/latest/>`_
is used.

OSCAd is tested with

* CPython 2.6
* CPython 2.7
* CPython 3.2
* CPython 3.3
* PyPy 2.1 (Python 2.7)

When the documentation mentions the ``python`` binary it always means the binary
in your virtualenv. So be sure to activate the virtualenv or specify the absolut
path to the binary. For more information about virtualenv take a look at
http://www.virtualenv.org/

Installation
------------

* Make sure ``virtualenv`` and ``pip`` are installed

.. code-block:: bash

    # apt-get install python-virtualenv python-pip

* Create and activate a new virtualenv

.. code-block:: bash

    $ cd $OSCAD_DIR
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -e .
    $ pip install waitress

* Start the application with the development configuration

.. code-block:: bash

    $ pserve development.ini

* Visit http://localhost:6543 in your browser

Tests
-----

* For the testsuite with all versions use ``tox``
* If testing a single version use ``python setup.py test``
* The tests will require additional packages, which will be installed
  automatically
* The integration tests will need a PHP version of
  `OSCAd <http://dtag-dbu.github.io/oscad/>`_ installed.
  As each run of the testsuite will issue >800 requests to that, so it is higly
  advisable to use a local instance for testing.
  The location of this instance has to be specfied in ``development.ini``

Translations
------------

To translate the application have a look at the ``locale`` directory in the
packages, most notably ``oscad/locale``.

The translation workflow is a standard gettext workflow eased by the integration
with the Babel translation toolkit.

The translation toolchain should be with used with Python 2 (not Python 3),
however the application itself also supports Python 3.

First we exctract translateable messages from the templates and code file.
This updates the global translations template ``oscad/locale/oscad.pot``.

.. code-block:: bash

    $ python setup.py extract_messages

Then update all the existing language specific message catalogs, or only a
single catalog:

.. code-block:: bash

    $ python setup.py update_catalog

    # or
    $ python setup.py update_catalog -l fr

This places updated catalogs in the subdirectories in ``oscad/locale/``.
You can edit them with your favourite gettext editor or as plaintext files
(you should know about the format then)

Now the updated catalogs can be compiled into binary files which can be read by
the application:

.. code-block:: bash

    $ python setup.py compile_catalog

It is also possible to create catalogs for new languages:

.. code-block:: bash

    $ python setup.py init_catalog -l es


Theming
-------

There are several ways to customize the appearance of the application via
themes.
A theme consists of a normal python module containing a set of static assets,
template (-snippets) or translations.
One theme is directly bundled with the application.
It is located in the directory ``oscad_theme_basic/``.
To be recognized as a python module it has to contain a file ``__init__.py``
which can be empty.

Builtin templates and static assets can be overridden shipping a resource of the
same name and type in a theme.
For possible ways of customization look for places in the code where templates
are loaded either via a template renderer or via template inclusion.
When overriding translations make sure to use the correct gettext domain.

As themes are normal packages they don't have to be in the applications source
tree to be used.
Just install them into your virtualenv or put them on ``sys.path``.

Themes are activated with the configuration directive ``themes``. The plural
form indicates, that it's possible to configure multiple cascading themes.
The value of the configuration directive is a whitespace delimited list of
theme names which should be importable.
Otherwise an exception is thrown at startup.
