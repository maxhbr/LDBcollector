#!/bin/sh
# SPDX-FileCopyrightText: 2022 Hermine-team <hermine@inno3.fr>
#
# SPDX-License-Identifier: AGPL-3.0-only

project_name=hermine

cmd=$1
[ -z "$cmd" ] && cmd=up

docker-compose -p hermine -f $(dirname $0)/docker-compose.yml $cmd
