#!/bin/bash

OPTS=`getopt -o "" --long debug -n $0 -- "$@"`
if [[ $? != 0 ]] ; then echo "Unable to parse options." 1>&2 ; exit 1 ; fi
eval set -- "$OPTS"

DEBUG=false

while true
do
  case "$1" in
    --debug )
      DEBUG=true
      shift
      ;;
    -- )
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done
  

cmd="avocado run ./check_modulemd.py"

if [[ $DEBUG = true ]]
then
    # For debugging the test script, the --show-job-log option causes avocado to
    # display only job log (instead of test summary) on stdout.
    cmd="$cmd --show-job-log"
fi

if [[ $# > 0 ]]
then
    # set avocado "modulemd" parameter to first shell argument
    cmd="$cmd --mux-inject 'run:modulemd:$1'"
fi

echo Running: "$cmd"
eval $cmd
