## Finos:
# Open Source License Compliance Handbook
This handbook provides information on how to comply with some of the more common open source licenses under a specific set of use-cases.
* raw data: https://github.com/finos/OSLC-handbook


## Example: Apache-2.0
```
# SPDX-License-Identifier: CC-BY-SA-4.0
-
  name: Apache Software License 2.0
  licenseId: Apache-2.0
  notes:
  terms:
  - type: condition
    description: Provide copy of license
    use_cases: [UB, MB, US, MS]
    compliance_notes: Does not specify format for providing copy of license

  - type: condition
    description: Notice of modifications
    use_cases: [MB, MS]
    compliance_notes: Modified files must include "prominent notices" of the modifications
    
  - type: condition
    description: Retain all notices
    use_cases: [US, MS]
    compliance_notes: Copyright notices and other notices do not have to be reproduced for binary distribution

  - type: condition
    description: Include NOTICE file with distribution
    use_cases: [UB, MB]
    compliance_notes: If a NOTICE is present, include it in any distribution of the work or derivative works (to the extent the NOTICE file appiles to the derivatives)

  - type: termination
    description: Any patent claims accusing the work by a licensee results in termination of all patent licenses to the licensee.
```