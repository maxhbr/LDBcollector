#!/bin/bash

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

exec_shell()
{
    COMMAND="$1"
    SHELL_ARGS="$2"
    printf "$COMMAND\nexit\n" | ./devel/flame shell $SHELL_ARGS
}

test_shell()
{
    COMMAND="$1"
    EXPECTED="$2"
    SHELL_ARGS="$3"

    echo -n "$COMMAND: "
    
    ACTUAL=$(exec_shell "$COMMAND" "$SHELL_ARGS")

    if [ "$ACTUAL" != "$EXPECTED" ]
    then
        echo
        echo "ERROR"
        echo "  command: $COMMAND"
        echo "  exepcted: $EXPECTED"
        echo "  actual:   $ACTUAL"
        exit 1
    fi

    echo "OK"
}

test_shell_silent()
{
    test_shell "$1" "$2" "-s"
}

# test command: license
test_shell_silent "license\nmit" "MIT"
test_shell_silent "license\nmit and mit" "MIT AND MIT"

# test command: simplify
test_shell_silent "simplify\nmit and mit" "MIT"
test_shell_silent "simplify\nGPL-2.0-only" "GPL-2.0-only"

# test command: unknown 
test_shell_silent "unknown\nsomeweirdlicense" "Unknown: Unknown symbols identified.
someweirdlicense"
test_shell_silent "unknown\nmit" ""
