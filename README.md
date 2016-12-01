# check_modulemd

This contains [avocado testing framework](http://avocado-framework.github.io/)
based tests to conduct various module checks.

* check_modulemd.py - check the validity of a modulemd file
* check_compose.py - check validity of module composition (_work in progress_)

## Setup

Install prerequisite RPMs if necessary:

* python2-aexpect - dependency for python-avocado
* python2-avocado - avocado testing framework
* python2-modulemd - Module metadata manipulation library
* python-enchant - spell checker library (needed only for check_modulemd.py)
* hunspell-en-US - English dictionary (needed only for check_modulemd.py)
* python2-dnf - Python 2 interface to DNF (needed only for check_compose.py)

## Running check_modulemd.py

Call avocado to run check_modulemd.py, providing the path to the modulemd file using
[avocado's parameter passing mechanism](http://avocado-framework.readthedocs.io/en/latest/WritingTests.html#accessing-test-parameters):

    avocado run ./check_modulemd.py --mux-inject 'run:modulemd:/path/to/modulemd.yaml'

For convenience during development of the test script, a wrapper script is
provided that simplifies passing the required parameter:

    ./run-checkmmd.sh [--debug] /path/to/modulemd.yaml


### Example modulemd files

Some example modulemd files can be obtained from the following locations:

* http://pkgs.stg.fedoraproject.org/cgit/modules/base-runtime.git/plain/base-runtime.yaml
* http://pkgs.stg.fedoraproject.org/cgit/modules/testmodule.git/plain/testmodule.yaml
* https://pagure.io/modulemd/raw/master/f/spec.yaml

### Taskotron

This check should eventually be called by [Taskotron](https://fedoraproject.org/wiki/Taskotron). A *non-working* start of a task definition has been included:

    runtask ./runtask.yml

## Running check_compose.py

Call avocado to run check_compose.py, providing the path to the composed
repository and the modulemd file using
[avocado's parameter passing mechanism](http://avocado-framework.readthedocs.io/en/latest/WritingTests.html#accessing-test-parameters):

    avocado run ./check_compose.py --mux-inject 'run:repo:/path/to/repository' 'run:modulemd:/path/to/modulemd.yaml'

For convenience during development of the test script, a wrapper script is
provided that simplifies passing the required parameters:

    ./run-checkcomp.sh [--debug] /path/to/repository /path/to/modulemd.yaml

