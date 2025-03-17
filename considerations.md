<!--
SPDX-FileCopyrightText: 2025 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Order of replacing alias, operators etc

## Approaches

### Update operators first

| License expression    | MIT OR GPL 2.0 or later      |
|-----------------------|------------------------------|
| update op             | MIT OR GPL 2.0 or later      |
| update expr           | MIT OR GPL-2.0-only OR later |
| Status                | Fail                         |


| License expression    | MIT&&GPLv2                   |
|-----------------------|------------------------------|
| update op             | MIT AND GPLv2                |
| update expr           | MIT AND GPL-2.0-only         |
| Status                | OK                           |

The examples above show that updating operators first and then expressions does not work.


### Expression first approach

| License expression    | MIT OR GPL 2.0 or later      |
|-----------------------|------------------------------|
| update expr           | MIT OR GPL-2.0-or-later      |
| update op             | MIT OR GPL-2.0-or-later      |
| Status                | OK                           |


| License expression    | MIT&&GPLv2                   |
|-----------------------|------------------------------|
| update expr           | MIT&&GPLv2                   |
| update op             | MIT AND GPLv2                |
| Status                | Fail                         |


The examples above show that updating expressions first and then operators does not work.

