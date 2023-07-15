# {metæffekt}-universe
Project providing insights on the {metæffekt} license database covering

* 2032 modelled license terms,
* 129 exceptions,
* 169 specific and commonly used license expressions, and
* 46 markers.

as of 24th, June 2023.

The following links provide letter-specific overviews on the license information:

[3](src/main/resources/ae-universe/[3]/README.md) -
[4](src/main/resources/ae-universe/[4]/README.md) -
[a](src/main/resources/ae-universe/[a]/README.md) -
[b](src/main/resources/ae-universe/[b]/README.md) -
[c](src/main/resources/ae-universe/[c]/README.md) -
[d](src/main/resources/ae-universe/[d]/README.md) -
[e](src/main/resources/ae-universe/[e]/README.md) -
[f](src/main/resources/ae-universe/[f]/README.md) -
[g](src/main/resources/ae-universe/[g]/README.md) -
[h](src/main/resources/ae-universe/[h]/README.md) -
[i](src/main/resources/ae-universe/[i]/README.md) -
[j](src/main/resources/ae-universe/[j]/README.md) -
[k](src/main/resources/ae-universe/[k]/README.md) -
[l](src/main/resources/ae-universe/[l]/README.md) -
[m](src/main/resources/ae-universe/[m]/README.md) -
[n](src/main/resources/ae-universe/[n]/README.md) -
[o](src/main/resources/ae-universe/[o]/README.md) -
[p](src/main/resources/ae-universe/[p]/README.md) -
[q](src/main/resources/ae-universe/[q]/README.md) -
[r](src/main/resources/ae-universe/[r]/README.md) -
[s](src/main/resources/ae-universe/[s]/README.md) -
[t](src/main/resources/ae-universe/[t]/README.md) -
[u](src/main/resources/ae-universe/[u]/README.md) -
[v](src/main/resources/ae-universe/[v]/README.md) -
[w](src/main/resources/ae-universe/[w]/README.md) -
[x](src/main/resources/ae-universe/[x]/README.md) -
[y](src/main/resources/ae-universe/[y]/README.md) -
[z](src/main/resources/ae-universe/[z]/README.md)

The yaml files within the subfolders show metadata on the individual licenses and exceptions.
The files also contain alternative names that support the normalization of licenses and exceptions.

## Why another list of licenses and exceptions?
{metæffekt} follows a defined strategy for analyzing, scanning and documenting software projects. To do this, a 
consistent information/data baseline is required. This baseline must cover the different license types that are used
by the software stacks being examined.

OSI, SPDX and the ScanCode Toolkit provide a good representation of licenses and exceptions in the FOSS domain. 
However, the license identification and matching strategies are not fully compatible with
the level of granularity and paradigms set forth by {metæffekt}. Second, the data does not cover publicly
available commercial licenses (at least not to the extend required).

This is why {metæffekt} choose to create an overarching database of licenses, 
references, exceptions, and expressions; the {metæffekt}-universe.

## Is {metæffekt} handing back to the FOSS Compliance Community?
Sure. We intend to provide those parts of our {metæffekt}-universe to the community, which we are allowed to share.

The only issue is time and resources. {metæffekt} is a self-financed company that makes a
living from customer projects. With our limited time and resources we have to be very focused. 
We are ready to do community work, once we see that there is an interest in our results.

So if you see that this material can be useful to you or ease your work, let us know. We are looking forward to
intensify our community engagement or to start off new projects.

## Disclaimer

This is all work in progress and subject to continuous improvement. In particular, ScanCode identifications and
ScanCode matching is used to validate the dataset and synchronize the different sources.

Please note that the {metæffekt}-universe as displayed in this repository is a converted, reduced
dataset from a more extensive internal representation. The internal representation models licenses
explicitly and is used for deterministic license matching based on evidences and patterns.

The internal representation (and therefore the content shown here) is based on SPDX and ScanCode.

All company names, organization names, license names, and product names mentioned in this documentation
are used for identification purposes only.

## Licensing

- [SPDX](https://spdx.org/licenses/) - The license list is used under 
  [Creative Commons BY-3.0](http://spdx.org/licenses/CC-BY-3.0).
  
  © 2018 SPDX Workgroup a Linux Foundation Project. All Rights Reserved.

- [ScanCode Toolkit](https://github.com/nexB/scancode-toolkit) - ScanCode license data is used under 
  [Creative Commons BY-4.0](https://github.com/nexB/scancode-toolkit/blob/develop/cc-by-4.0.LICENSE).

  Copyright (c) nexB Inc. and others. All rights reserved.
  ScanCode is a trademark of nexB Inc.

- [Open CoDE License Compliance](https://wikijs.opencode.de/de/Hilfestellungen_und_Richtlinien/Lizenzcompliance) 
  approval information is Open CoDE Public Domain. The status information shown reflects version 1.0 from
  February 2022.

The content provided in {metæffekt}-universe is licensed under [Creative Commons BY-4.0](LICENSE).

Copyright © metaeffekt GmbH 2021. All rights reserved.

## Contribution
As this repository is largely showing converted data a direct contribution in the form of patches is
not appropriate. You may send requests for corrections or questions 
to [contact@metaeffekt.com](mailto:contact@metaeffekt.com). Modifications will then be applied to the 
internal dataset to produce the corrected outputs.

## Further information
{metæffekt} provides visualization of the {metæffekt}-universe on https://metaeffekt.com/#universe.

Currently, ScanCode version 31.2.1 is used.

Non-approved OSI status information is not yet complete; more details will be added short-term.
Please note in this context, that all OSI status details except `approved` convey unofficial information collected
from mailing lists and other public available OSI-centric sources and are subject to interpretation. In the perspective
of risk-based license assessment and evaluating OSI compliance of software, the information is yet considered useful to
indicate potential issues. 

The following table summarizes and details the OSI status values:

| OSI Status Value | Description                                                                                                                     | Official OSI Status |
|:-----------------|:--------------------------------------------------------------------------------------------------------------------------------|:--------------------|
| not submitted    | The license appears on the non-approved licenses as [not submitted].                                                            | no                  |
| submitted        | The license has been submitted or at least requested, but has not yet been further processed.                                   | no                  |
| pending          | The license is in discussion / review. No decision is available yet.                                                            | no                  |
| approved         | The license was officially approved by OSI.                                                                                     | yes                 |
| withdrawn        | The license was withdrawn by the submitter (i.e. the license stuart).                                                           | no                  |
| rejected         | The license was rejected by OSI. The license is either not valid license or does not conform to the OSI Open Source Definition. | no                  |
| ineligible       | The terms are not considered a (software) license or show obvious conditions adverse to the OSI Open Source Definition.         | no                  |

Regarding SPDX the latest version from https://github.com/spdx/license-list-data
main branch is used to synchronize the {metæffekt}-universe.