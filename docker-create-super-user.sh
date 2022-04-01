#!/bin/sh
# SPDX-FileCopyrightText: 2022 Hermine-team <hermine@inno3.fr>
#
# SPDX-License-Identifier: AGPL-3.0-only

project_name=hermine

docker exec -it ${project_name}_web_1 /opt/bitnami/python/bin/python /opt/hermine/manage.py createsuperuser
