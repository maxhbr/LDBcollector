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

### OSI license List
The OSI license list is imported via the `opensource` haskell package.

### Scancode license List
The scancode data is placed in `/data/scancode/` and contains the content of the folder `/src/licensedcode/data/licenses/**` from [https://github.com/nexB/scancode-toolkit**.

**licensed under:** cc0-1.0

### Wikipedia comparison of licenses
The table for general comparison of licenses is taken from https://en.wikipedia.org/wiki/Comparison_of_free_and_open-source_software_licenses and is placed in the source file.

The corresponding data is hardcoded in source code, right now.

### OSADL license checklist
The folder `/data/OSADL/` contains a script `dump.sh` which pulls the checklist stuff. The sources for that are for example
e.g.
- https://www.osadl.org/fileadmin/checklists/unreflicenses/GPL-2.0-only.txt
- https://www.osadl.org/fileadmin/checklists/actions/Forward.txt
- https://www.osadl.org/fileadmin/checklists/actions/ACTION.txt
The complete list can be found at: https://www.osadl.org/Access-to-raw-data.oss-compliance-raw-data-access.0.html

### ChooseALicense.com licenses
The folder `/data/choosalicense` contains the conten of the folder `/_licenses/` from [https://github.com/github/choosealicense.com**.

**licensed under:** MIT

### Blue Oak Council License List
The license list can be pulled from https://blueoakcouncil.org/list.json, and is placed at `data/blue-oak-council-license-list.json**

**licensed under:** CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

### Fedora Project Wiki
The Fedora Project has in its wiki a list of licenses which are rated **good** or **bad** on [https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing].
These lists are extracted to csv files in `/data/Fedora_Project_Wiki/`.

#### TODO: the Fedora project also has notes regarding to licenses
- e.g. https://fedoraproject.org/wiki/Licensing/Sleepycat

### Open Chain Policy Template
The open chain project published an example policy as a spreadsheet on [https://www.openchainproject.org/news/2019/01/17/openchain-open-source-policy-template-now-available].
From the spreadsheet page "Example Appendix 1 - Unofficial License Grid used by UK Entity" one can extract the license list into a CSV file

### OSLC-Handbook
[OSLC-handbook](https://github.com/finos-osr/OSLC-handbook/tree/master/src**

The fixed data can be found at https://github.com/maxhbr/OSLC-handbook/

**Licensed unnder:** CC-BY-SA-4.0

### google:
https://opensource.google.com/docs/thirdparty/licenses/

they classify licenses into: 
- restricted licenses
- restricted_if_statically_linked license
- reciprocal licenses
- notice licenses
- permissive licenses
- by_exception_only licenses

**licensed under:** CC-BY-4.0

### Open Knowledge International
https://github.com/okfn/licenses/blob/master/licenses.csv

The corresponding raw data is placed under `./data/okfn-licenses.csv`

**licensed under:** ODC Public Domain Dedication and Licence (PDDL) / MIT

### DFSG License list
https://wiki.debian.org/DFSGLicenses / https://www.debian.org/legal/licenses/

### FSF / GNU License list
FSF: [gnu.org](https://www.gnu.org/licenses/license-list.html)

**licensed under:** MIT

### ifrOSS
- https://github.com/ifrOSS/ifrOSS
- https://ifross.github.io/ifrOSS/Lizenzcenter

The corresponding data is hardcoded in source code, right now.

**licensed under:** MIT / ODbL

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
