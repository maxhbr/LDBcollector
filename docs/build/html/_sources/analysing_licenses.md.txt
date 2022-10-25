<!---
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr>
SPDX-License-Identifier: CC-BY-4.0
-->

# Analysing licenses

One goal of Hermine is to help you analyse FOSS licenses in a consistent and systematic way.
The analysis of a license is divided in two parts:

- The global characterics of the license
- Its decomposition into different obligations.

## Global characterics

### Identity of the license

- SPDX ID = The [short SPDX ID](https://spdx.dev/ids/) of the license. In case an exception is added,
this field would inlcude it. E.g. : `GPL-3.0-only WITH GCC-exception-3.1`
- Long name = The full name, as defined by the SPDX standard
- url = The reference URL of the license
- verbatim = The whole text of the license, in case it is not referenced on the SPDX website.
- copyleft = The type of reciprocity clause of the license ; possible choices are: Persmissive, Strong copyleft, Weak copyleft, Strong network copyleft, Weak network copyleft  
- law_choice = The choice of applicable law 
- venue_choice = The choice of venue
- liability = If the license has a non-liability clause
- warranty = If the license has a warranty limitation clause

### Policy 
- Status = The review status of the license,
- allowed = The acceptability of the license;  possible choices are: Always allowed (Green), Never allowed (Red), Allowed depending on the context (Organge) (and Grey for "Not reviewed yet")
- allowed_explanation = The motivation for non green choices, and the acceptable contexts for orange licenses. 
- comment = Any relevant comments for understanding the interpretation of the license

### Conditions of use

- patent_grant = True when the license contains a patent grant, along the copyright grant.
- ethical_clause = If the license contains an ethical clause (e.g. the JSON License)
- Only non-commercial use = if the license allows only non-commercial uses (e.g. Creative commons with a NC clause) 


### Other optional information

- categories = Currently, it is just a text to receive free text, that could be a comma separated list, for instance.
- license_version = The version of the license (e.g. "2.1" for LGPL-2.1-only). 
- radical = The root of the name of the license (e.g. "LGPL" for LGPL-2.1-only).
- autoupgrade = True if the license authorize to apply latter versions of the license (e.g. : False for LGPL-2.1-only and True for LGPL-2.1-or-later) 
- steward = The name of the entity that is allowed to create new versions of the license (e.g. : the Eclipse Foundation for the EPL-2.0)
- inspiration_spdx = The license that served as inspiration for the analysed license, mentionned by its SPDX ID, in case it's not regitered in Hermine   
- inspiration = The license that served as inspiration for the analysed license, in case it's regitered in Hermine 
- osi_approved = If the license has been approved by the OSI
- fsf_approved = If the license has been approved by the FSF
- foss = If the license if considered Free or Open Source software. Possible values are We consider it is FOSS, We consider it is NOT FOSS, FOSS - deduced (when it's approved by the FSF or the OSI), NOT FOSS - deduced (when the FSF or the OSI have explicitely declared it as such)  
- non_tivoisation = True if the license contains a clause against [tivoization](https://en.wikipedia.org/wiki/Tivoization) (e.g. GPL-3.0-only)




## Obligations and generic obligations

### License obligations

#### Text of the obligations

For each license that you analyse, you can extract from its text the part that is relevant to each indiviofual obligation.
For instance, in the BSD-3-Clause, you would would copy in this :

>  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

#### Passivity of the obligation

Some obligations will require that you perform a specific action to be in compliance with the license.
We call them _Active_ obligations.

For instance, in the BSD-3-Clause, the following obligation is active:

> 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

While others, will require that you refrain from doing something.
We call them _Passive_ obligations.

For instance, in the BSD-3-Clause, the following obligation is passive:

>  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#### Triggers of the obligation

An active obligation can be triggered by the combination of two factors. The first one is related to the exploitation of the software, the second one to its modification status. 

- **Exploitation**: This indicates if the obligations for the following 
  - Distribution as source code
  - Distribution as non source form
  - Providing access through the network  

If an obligation is triggered by two different types of exploitation, you'll have to create two instances of this obligation, one for each triggering scenario.

- **Modification**: This indicates if the obligations applies only if the component is modified, only if it is not modified or in both cases.

### Generic obligations

A license obligation can be related to a generic obligation. A generic obligation is a way to group license obligations that would amount to the same operational actions.


### Core set of generic obligations

Some generic obligations are very common and have a low cost of implementations. It appears often more effective to honor for every license, even if the license doesn't explicitely require it. 
We called the set of such generic obligations "core generic obligations".
So if a release of a product has all its generic obligations in the core, you know that you don't have any specific action to perform to reach compliance.




