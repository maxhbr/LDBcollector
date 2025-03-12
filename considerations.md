
# Operator first approach

| License expression    | MIT OR GPL 2.0 or later      |
|-----------------------|------------------------------|
| fix op                | MIT OR GPL 2.0 or later      |
| fix expr              | MIT OR GPL-2.0-only OR later |
| Status                | Fail                         |


| License expression    | MIT&&GPLv2                   |
|-----------------------|------------------------------|
| fix op                | MIT AND GPLv2                |
| fix expr              | MIT AND GPL-2.0-only         |
| Status                | OK                           |




# Expression first approach

| License expression    | MIT OR GPL 2.0 or later      |
|-----------------------|------------------------------|
| fix expr              | MIT OR GPL-2.0-or-later      |
| fix op                | MIT OR GPL-2.0-or-later      |
| Status                | OK                           |


| License expression    | MIT&&GPLv2                   |
|-----------------------|------------------------------|
| fix expr              | MIT&&GPLv2                   |
| fix op                | MIT AND GPLv2                |
| Status                | Fail                         |



