<!---
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr>
SPDX-License-Identifier: CC-BY-4.0
-->

# Defining a FOSS policy

One goal of Hermine is to help define a FOSS policy by providing a framework to analyse FOSS licences in a consistent and systematic way.  
The analysis of a licence is divided in three parts:

- The global characterics of the licence
- For licences that are only authorized in specific contexts, the list of authorized contexts
- Its decomposition into different obligations.

## Global characterics of licences

### Characterics pertaining to the identity of the licence

**SPDX Identifier:**  
The [short SPDX ID](https://spdx.dev/ids/) of the licence, including possible exceptions.  
E.g. : `GPL-3.0-only WITH GCC-exception-3.1`

**Name:**  
The full name, as defined by the SPDX standard

**Url:**  
The reference URL of the licence

**Copyleft:**  
The type of reciprocity clause of the licence.  
Possible choices are:
  - Persmissive
  - Strong copyleft
  - Weak copyleft
  - Strong network copyleft
  - Weak network copyleft

**FOSS:**  
If the licence if considered *Free or Open Source software*.  
Possible values are:
  - We consider it is FOSS
  - We consider it is NOT FOSS
  - FOSS - deduced (when it's approved by the FSF or the OSI)
  - NOT FOSS - deduced (when the FSF or the OSI have explicitely declared it as such)

**Law choice:**  
The choice of applicable law

**Venue choice:**  
The choice of venue

**Disclaimer of Warranty:**  
If the licence has a warranty disclaimer

**Limitation of Liability:**  
If the licence has a non-liability clause

**Exact text of the license:**  
The whole text of the licence, in case it is not referenced on the SPDX website.

### Foss Policy 

**Review status**  
The possible choices are:
- To check
- Checked
- To discuss
- Pending

**OSS Policy**  
The acceptability of the licence.  
Possible choices are:
- Always allowed (Green)
- Never allowed (Red)
- Allowed depending on the context (Orange)

Note: the Policy will remain Grey until it has been reviewed

**OSS Policy explanation**  
The motivation for non green choices, and the acceptable contexts for orange licences. 

**Comment**  
To explain the interpretation of the licence

### Conditions of use

**Patent grant**  
True if the licence contains a patent grant, along with the copyright grant.

**Ethical clause**  
True if the licence contains an ethical clause (e.g. the JSON Licence)

**Only non-commercial use**  
True if the licence allows only non-commercial uses (e.g. Creative commons with a NC clause)


### Other optional information

The information below can be usefull, but is considered secondary from an operational point of view (only available in the Django Admnin interface).

- **categories:** Currently, it is just a text to receive free text, that could be a comma separated list, for instance.
- **license_version:** The version of the licence (e.g. "2.1" for LGPL-2.1-only). 
- **radical:** The root of the name of the licence (e.g. "LGPL" for LGPL-2.1-only).
- **autoupgrade:** True if the licence authorise to apply latter versions of the licence (e.g. : False for LGPL-2.1-only and True for LGPL-2.1-or-later) 
- **steward:** The name of the entity that is allowed to create new versions of the licence (e.g. : the Eclipse Foundation for the EPL-2.0)
- **inspiration_spdx:** The licence that served as inspiration for the analysed licence, mentionned by its SPDX ID, in case it's not registered in Hermine   
- **inspiration:** The licence that served as inspiration for the analysed licence, in case it's registered in Hermine 
- **osi_approved:** If the licence has been approved by the OSI
- **fsf_approved:** If the licence has been approved by the FSF
- **non_tivoisation:** True if the licence contains a clause against [tivoization](https://en.wikipedia.org/wiki/Tivoization) (e.g. GPL-3.0-only)

## Authorised contexts
For licences that are allowed only in certain contexts, it is possible to define them automatically if they only depend on technical criteria:
- The type of linking between the dependency and your own code
- The type of exploitation that will be made of the dependency
- The modification status of the dependency
- The scope in which the dependency is used
- A category to which the product belongs


## Obligations and generic obligations

### Licence obligations

#### Text of the obligations

For each licence that you analyse, you can extract from its text the part that is relevant to each individual obligation.
For instance, in the BSD-3-Clause, this would be typed :

>  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

#### Passivity of the obligation

**Active Obligations**

Obligations that require specific actions to be in compliance with the licence.

For instance, in the BSD-3-Clause, the following obligation is active:

> 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

**Passive Obligations**

Obligations that require that you refrain from doing something.

For instance, in the BSD-3-Clause, the following obligation is passive:

>  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#### Triggers of the obligation

An active obligation can be triggered by the combination of two factors. The first one is related to the exploitation of the software, the second one to its modification status. 

- **Exploitation**: Indicates which scenario triggers the obligation
  - Distribution as source code
  - Distribution as non source form
  - Providing access through the network  

If an obligation is triggered by two different types of exploitation, you'll have to create two instances of this obligation, one for each triggering scenario.

- **Modification**: Indicates if the obligations applies only if the component is modified, only if it is not modified or in both cases.

### Generic obligations

A licence obligation can be related to a generic obligation. A generic obligation is a way to group licence obligations that would amount to the same operational actions.

### Core set of generic obligations

Some generic obligations are very common and have a low cost of implementations. It appears often more effective to honor for every licence, even if the licence doesn't explicitely require it.  

The set of such generic obligations are named "core generic obligations".

So if a release of a product has all its generic obligations in the core, you know that you don't have any specific action to perform to reach compliance.




