# check_modulemd

This contains an [avocado testing framework](http://avocado-framework.github.io/)
based test to check the validitity of a modulemd file.

It is currently just a skeleton that verifies a 'modulemd' parameter has been
passed via avocado and that the parameter refers to a file that exists.

## Setup

Install avocado and its dependencies.

## Running

Call avocado to run check_modulemd.py, providing the path to the modulemd file using
[avocado's parameter passing mechanism](http://avocado-framework.readthedocs.io/en/latest/WritingTests.html#accessing-test-parameters):

    avocado run ./check_modulemd.py --mux-inject 'run:modulemd:/path/to/modulemd'

For convenience during development of the test script, a wrapper script is
provided that simplifies passing the required parameter:

    ./run-check.sh /tmp/to/modulemd

## Taskotron

This check should eventually be called by [Taskotron](https://fedoraproject.org/wiki/Taskotron). A *non-working* start of a task definition has been included:

    runtask ./runtask.yml
