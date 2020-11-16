# LDBcollector

The generated output is pushed to the branch [`generated`](https://github.com/maxhbr/LDBcollector/tree/generated).

## Produced Output:
- JSON
- Markdown
- Org-Mode
- AsciiDoc
- HTML

### Other endpoints:
- sync to Confluence (planned)

## Consumed Data (implemented)
### SPDX license List
The data is placed in `/data/json/` and it contains the content of the folder `/json/` from [https://github.com/spdx/license-list-data].

|-----------------|---|
| Kind of update: | ./data/spdx-license-list-data.update.sh |
| Last update:    | 2020-11-15                              |
| Version:        | 3.10-24-gd78ad74                        |

### OSI license List
The OSI license list is imported via the `opensource` haskell package.

| Kind of Update | pulled on runtime via `opensource` haskell package |

### Scancode license List
The scancode data is placed in `/data/scancode/` and contains the content of the folder `/src/licensedcode/data/licenses/` from https://github.com/nexB/scancode-toolkit.

**licensed under:** cc0-1.0

|-----------------|---|
| Kind of update: | ./data/nexB_scancode-toolkit_license_list.update.sh                                      |
| Last update:    | 2020-11-15                                                                               |
| Version:        | https://github.com/nexB/scancode-toolkit/commit/ba4bbf216c6f44572662d16c76214a08b0a69e7e |

### Wikipedia comparison of licenses
The table for general comparison of licenses is taken from https://en.wikipedia.org/wiki/Comparison_of_free_and_open-source_software_licenses and is placed in the source file.

The corresponding data is hardcoded in source code, right now.

|-----------------|---|
| Kind of update: | manual labor |

### OSADL license checklist
The folder `/data/OSADL/` contains a script `dump.sh` which pulls the checklist stuff. The sources for that are for example
e.g.
- https://www.osadl.org/fileadmin/checklists/unreflicenses/GPL-2.0-only.txt
- https://www.osadl.org/fileadmin/checklists/actions/Forward.txt
- https://www.osadl.org/fileadmin/checklists/actions/ACTION.txt
The complete list can be found at: [https://www.osadl.org/Access-to-raw-data.oss-compliance-raw-data-access.0.html]

|-----------------|---|
| Kind of update: | ./data/OSADL.update.sh |
| Last update:    | 2020-11-15             |
| Version:        |                        |


### ChooseALicense.com licenses
The folder `/data/choosealicense.com` contains the content of the folder `/_licenses/` from https://github.com/github/choosealicense.com.

**licensed under:** MIT

|-----------------|---|
| Kind of update: | ./data/choosalicense.com.update.sh                                                           |
| Last update:    | 2020-11-15                                                                                   |
| Version:        | https://github.com/github/choosealicense.com/commit/50e1c110548545b3ec5072442942be2548a76a48 |

### Blue Oak Council License List
The license list can be pulled from https://blueoakcouncil.org/list.json, and is placed at `data/blue-oak-council-license-list.json`. The copyleft list is from https://blueoakcouncil.org/copyleft.json and placed at `data/blue-oak-council-copyleft-list.json`

**licensed under:** CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

|-----------------|---|
| Kind of update: | ./data/blue-oak-council.update.sh |
| Last update:    | 2020-11-15                        |
| Version:        |                                   |

### Fedora Project Wiki
The Fedora Project has in its wiki a list of licenses which are rated **good** or **bad** on https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing.
These lists are extracted to csv files in `/data/Fedora_Project_Wiki/`.

|-----------------|---|
| Kind of update: | manual labor |

#### TODO: the Fedora project also has notes regarding to licenses
- e.g. https://fedoraproject.org/wiki/Licensing/Sleepycat

### Open Chain Policy Template

|-----------------|---|
| Kind of update: | manual labor |
| Version:        | 1.2          |

#### Version 1.2
The open chain project published an example policy as a spreadsheet on [openchain-open-source-policy-template-now-available](https://www.openchainproject.org/news/2019/01/17/openchain-open-source-policy-template-now-available).
From the spreadsheet page **"Example Appendix 1 - Unofficial License Grid used by UK Entity"** one can extract the license list into a CSV file

#### Update: version 2.0
https://www.openchainproject.org/news/2019/12/11/open-source-policy-template-2-0-in-chinese-traditional-and-english

This template only contains 10 licenses...

### OSLC-Handbook
[OSLC-handbook](https://github.com/finos-osr/OSLC-handbook/tree/master/src)

**Licensed unnder:** CC-BY-SA-4.0

|-----------------|---|
| Kind of update: | ./data/OSLC-handbook.update.sh                                                         |
| Last update:    | 2020-11-15                                                                             |
| Version:        | https://github.com/finos/OSLC-handbook/commit/eafdcdac855a0e1877606eb15eba561b2abf0dba |

### Google Open Source Policy:
https://opensource.google.com/docs/thirdparty/licenses/

they classify licenses into: 
- restricted licenses
- restricted_if_statically_linked license
- reciprocal licenses
- notice licenses
- permissive licenses
- by_exception_only licenses

**licensed under:** CC-BY-4.0

|-----------------|---|
| Kind of update: | manual labor |
| Last update:    |              |
| Version:        |              |

### Open Knowledge International
https://github.com/okfn/licenses/blob/master/licenses.csv

The corresponding raw data is placed under `./data/okfn-licenses.csv`

**licensed under:** ODC Public Domain Dedication and Licence (PDDL) / MIT

|-----------------|---|
| Kind of update: | ./data/okfn-licenses.update.sh                                                   |
| Last update:    | 2020-11-15                                                                       |
| Version:        | https://github.com/okfn/licenses/commit/cc05e0a3be9490cfcb02fc664c46619846ee3752 |

### DFSG License list
https://wiki.debian.org/DFSGLicenses / https://www.debian.org/legal/licenses/

|-----------------|---|
| Kind of update: | ? |

### FSF / GNU License list
FSF: [gnu.org](https://www.gnu.org/licenses/license-list.html)

**licensed under:** MIT

|-----------------|---|
| Kind of update: | ? |

### ifrOSS
- https://github.com/ifrOSS/ifrOSS
- https://ifross.github.io/ifrOSS/Lizenzcenter

The corresponding data is hardcoded in source code, right now.

**licensed under:** MIT / ODbL

|-----------------|---|
| Kind of update: | ? |

## Other possible Sources for license Metadata
  - ORT License highlighting
  - ...
  - FOSSology
    data-license: GPL-2.0-only
  - ...
  - https://www.kanzlei-jun.de/wuerzburger-taxonomie.pdf
    - might not contain the right kind of content
  - ~~tldrlegal.com~~
    - Can not be used, licensing is unclear.
  - EUPL kompatible lizenzen: https://joinup.ec.europa.eu/collection/eupl/eupl-compatible-open-source-licences
  - https://vvlibri.org/fr/guide-de-lauteur-libre-gerer-des-licences-differentes-compatibilites-de-licences/tableau-de
  - https://github.com/openSUSE/cavil under GPL-2.0
