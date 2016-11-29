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
  

cmd="avocado run ./check_compose.py"

if [[ $DEBUG = true ]]
then
    # For debugging the test script, the --show-job-log option causes avocado to
    # display only job log (instead of test summary) on stdout.
    cmd="$cmd --show-job-log"
fi

muxinject=""
if [[ $# > 0 ]]
then
    # set avocado "repo" parameter to first shell argument
    muxinject="$muxinject 'run:repo:$1'"
fi
if [[ $# > 1 ]]
then
    # set avocado "modulemd" parameter to second shell argument
    muxinject="$muxinject 'run:modulemd:$2'"
fi

if [ -n "$muxinject" ]
then
    cmd="$cmd --mux-inject $muxinject"
fi

echo Running: "$cmd"
eval $cmd
