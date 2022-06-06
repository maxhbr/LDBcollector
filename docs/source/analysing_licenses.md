<!---
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr>
SPDX-License-Identifier: CC-BY-4.0
-->

# Analysing licenses

One goal of Hermine is to help you analyse FOSS licences in a consistent and systematic way.
The analysis of a licence is divided in two parts:

- The global characterics of the licence
- Its decomposition into different obligations.

## Global characterics

- SPDX ID = The [short SPDX ID](https://spdx.dev/ids/) of the licence. In case an exception is added,
this field would inlcude it. E.g. : `GPL-3.0-only WITH GCC-exception-3.1`
- Status = The review status of the licence,
- Long name = The full name, as defined by the SPDX standard
- categories = Currently, it is just a text to receive free text, that could be a comma separated list, for instance.
- license_version = The version of the licence (e.g. "2.1" for LGPL-2.1-only). 
- radical = The root of the name of the licence (e.g. "LGPL" for LGPL-2.1-only).
- autoupgrade = True if the license authorize to apply latter versions of the license (e.g. : False for LGPL-2.1-only and True for LGPL-2.1-or-later) 
- steward = The name of the entity that is allowed to create new versions of the license (e.g. : the Eclipse Foundation for the EPL-2.0)
- inspiration_spdx = The license that served as inspiration for the analysed license, mentionned by its SPDX ID, in case it's not regitered in Hermine   
- inspiration = The license that served as inspiration for the analysed license, in case it's regitered in Hermine
- copyleft = The type of reciprocity clause of the license ; possible choices are: Persmissive, Strong copyleft, Weak copyleft, Strong network copyleft, Weak network copyleft  
- color = The acceptability of the license;  possible choices are: Always allowed (Green), Never allowed (Red), Allowed depending on the context (Organge) (and Grey for "Not reviewed yet")
- color_explanation = The motivation for non green choices, and the acceptable contexts for orange licenses. 
- url = The reference URL of the license
- osi_approved = If the license has been approved by the OSI
- fsf_approved = If the license has been approved by the FSF
- foss = If the license if considered Free or Open Source software. Possible values are We consider it is FOSS, We consider it is NOT FOSS, FOSS - deduced (when it's approved by the FSF or the OSI), NOT FOSS - deduced (when the FSF or the OSI have explicitely declared it as such)  
- patent_grant = True when the license contains a patent grant, along the copyright grant.
- ethical_clause = If the license contains an ethical clause (e.g. the JSON License)
- Only non-commercial use = if the license allows only non-commercial uses (e.g. Creative commons with a NC clause) 
- Legal uncertainty = True if you consider that the text of the licence is ambiguous or misses key elements (canonical example is WTFPL).
- non_tivoisation = True if the license contains a clause against [tivoization](https://en.wikipedia.org/wiki/Tivoization) (e.g. GPL-3.0-only)
- technical_nature_constraint = True if the license contains a clause on technincal nature of derivative works (e.g. LGPL-2.1-only)
- law_choice = The choice of applicable law 
- venue_choice = The choice of venue
- comment = Any relevant comments for understanding the interpretation of the license
- verbatim = The whole text of the license


## Obligations and generic obligations

### Licence obligations

#### Text of the obligations

For each licence that you analyse, you can extract from its text the part that is relevant to each indiviofual obligation.
For instance, in the BSD-3-Clause, you would would copy in this :

>  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

#### Passivity of the obligation

Some obligations will require that you perform a specific action to be in compliance with the licence.
We call them _Active_ obligations.

For instance, in the BSD-3-Clause, the following obligation is active:

> 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

While others, will require that you refrain from doing something.
We call them _Passive_ obligations.

For instance, in the BSD-3-Clause, the following obligation is passive:

>  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#### Triggers of the obligation

- Exploitation:

- Modification:

### Generic obligations

A license obligation can be related to a generic obligation. A generic obligation is a way to group license obligations that would amount to the same operational actions.


### Core set of generic obligations

Some generic obligations are very common and have a low cost of implementations. It appears often more effective to honor for every licence, even if the license doesn't explicitely require it. 
We called the set of such generic obligations "core generic obligations".
So if a release of a product has all its generic obligations in the core, you know that you don't have any specific action to perform to reach compliance.


