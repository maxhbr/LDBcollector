# check_modulemd

This contains [avocado testing framework](http://avocado-framework.github.io/)
based tests to conduct various module checks.

* check_modulemd.py - check the validity of a modulemd file

## Setup

Install prerequisite RPMs if necessary:

* pdc-client
* python2-aexpect - dependency for python-avocado
* python2-avocado - avocado testing framework
* python2-avocado-plugins-varianter-yaml-to-mux - parse YAML file into variants (Required for avocado-51.0 or later)
* python2-modulemd - Module metadata manipulation library
* python2-requests - HTTP library
* python-enchant - spell checker library
* hunspell-en-US - English dictionary
* modularity-testing-framework - MTF support (read modulemd files from config)

e.g.

    dnf install -y python2-aexpect \
    python2-avocado python2-avocado-plugins-varianter-yaml-to-mux \
    python2-modulemd python2-requests python-enchant \
    hunspell-en-US python2-pdc-client \
    modularity-testing-framework python2-dnf

## Running check_modulemd.py

Call avocado to run check_modulemd.py, providing the path to the modulemd file using
[avocado's parameter passing mechanism](http://avocado-framework.readthedocs.io/en/latest/WritingTests.html#accessing-test-parameters):

    avocado run ./check_modulemd.py --mux-inject 'run:modulemd:/path/to/modulemd.yaml'

In order to use a custom list of packaging jargon in the spell-checker, an optional additional parameter may be passed. This can be done by also providing the path to the jargon file on the command line:

    avocado run ./check_modulemd.py --mux-inject 'run:modulemd:/path/to/modulemd.yaml' 'run:jargonfile:/path/to/jargon.txt'

or by providing both the modulemd and jargonfile parameters using a multiplexer yaml file like the one used in this example:

    avocado run ./check_modulemd.py -m examples-testdata/params-checkmmd.yaml

For convenience during development of the test script, a wrapper script is
provided that simplifies passing the required parameter:

    ./run-checkmmd.sh [--debug] /path/to/modulemd.yaml

You can run project also as part of Modularity Testing Framework.
It will read modulemd files from config file and and can be scheduled as one of tests.
Jargon file can be passed via env variable JARGONFILE=/path/to/jargon.txt or
as multiplex value

     avocado run ./check_modulemd.py


You can also use provided Dockerfile:

    docker build --tag=$USER/check-modulemd .

And use it:

    docker run -ti -v $PWD/$MODULE.yaml:/$MODULE.yaml $USER/check-modulemd



### Example modulemd files

Some example modulemd files can be obtained from the following locations:

* http://pkgs.fedoraproject.org/cgit/modules/base-runtime.git/plain/base-runtime.yaml
* http://pkgs.fedoraproject.org/cgit/modules/testmodule.git/plain/testmodule.yaml
* https://pagure.io/modulemd/raw/master/f/spec.yaml

## Taskotron

This check is executed by [Taskotron](https://fedoraproject.org/wiki/Taskotron), see [results](https://taskotron.fedoraproject.org/resultsdb/results?&testcases=dist.modulemd).

### Running locally

You can run the same locally by running the ansible playbook. Execute the
following command as root (don't do this on a production machine!)::

  $ ansible-playbook tests.yml -e taskotron_item=<distgit_id>

and replace ``<distgit_id>`` with value in the form of ``namespace/name#gitref``.

For example::

  $ ansible-playbook tests.yml -e taskotron_item=modules/perl-bootstrap#cb3ea78913715df3e5b44e91ec2e464a61be918d

You can see the results in ``./artifacts/`` directory.

Alternatively you can run the task through Taskotron runner::

  $ runtask --item <distgit_id> --type dist_git_commit check_modulemd/

Don't forget to use ``--ssh`` or ``--libvirt``, otherwise you need to run this
as root (not recommended).
