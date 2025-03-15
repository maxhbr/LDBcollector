
# Replacing alias, operators etc

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



