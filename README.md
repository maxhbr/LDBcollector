# check_modulemd

This contains [avocado testing framework](http://avocado-framework.github.io/)
based tests to conduct various module checks.

* check_modulemd.py - check the validity of a modulemd file

## Setup

Install prerequisite RPMs if necessary:

* python2-aexpect - dependency for python-avocado
* python2-avocado - avocado testing framework
* python2-modulemd - Module metadata manipulation library
* python-enchant - spell checker library 
* hunspell-en-US - English dictionary 

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

You can also use provided Dockerfile:

    docker build --tag=$USER/check-modulemd .

And use it:

    docker run -ti -v $PWD/$MODULE.yaml:/$MODULE.yaml $USER/check-modulemd



### Example modulemd files

Some example modulemd files can be obtained from the following locations:

* http://pkgs.stg.fedoraproject.org/cgit/modules/base-runtime.git/plain/base-runtime.yaml
* http://pkgs.stg.fedoraproject.org/cgit/modules/testmodule.git/plain/testmodule.yaml
* https://pagure.io/modulemd/raw/master/f/spec.yaml

### Taskotron

This check should eventually be called by [Taskotron](https://fedoraproject.org/wiki/Taskotron). A *non-working* start of a task definition has been included:

    runtask -i "modules/testmodule#aaca87a82c35c1f0eb85556191f09f8a842abd9f" -t dist_git_commit -a noarch ./runtask.yml

