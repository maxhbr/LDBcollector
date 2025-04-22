<!---
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr>
SPDX-License-Identifier: CC-BY-4.0
-->

# Defining a FOSS policy

One goal of Hermine is to help define a FOSS policy by providing a framework to analyze FOSS licenses in a consistent and systematic way.  
The analysis of a license is divided in three parts:

- The global characteristics of the license
- For licenses that are only authorized in specific contexts, the list of authorized contexts
- Its decomposition into different obligations.

## Global characteristics of licenses

### Characteristics pertaining to the identity of the license

**SPDX Identifier:**  
SPDX is an open standard for communicating software bill of material information, including components, licenses, copyrights, and security references. SPDX short-form identifiers permits to communicate FOSS license information in a simple, efficient, portable and machine-readable manner.

**Copyright notice:**
Copyright notice is a legal form of notice to inform the public that the work is protected by copyright law and potentially gives information about the copyright owner, the date of publication etc.   
**Copyleft:**  
This clause present in the Open Source licenses imposes to the one who uses and/or modifies a component under the aforementioned license to redistribute/use it under the terms of the same license.  
Possible choices are:
  - Permissive: When the open source license does not require redistribution/reuse of the component under the terms of the same agreement.
  - Strong copyleft: Derivative works or works based on the Open Source Software must be distributed under the initial license or another license approved by the initial license.
  - Weak copyleft: Redistribution of the software or work, modified or not, can only be done under the initial license, but new components can be added under other licenses, see proprietary license.
  - Strong network copyleft: Derivative works or works based on the Open Source Software must be made available to users interacting with your application remotely through a computer network under the initial license or another license approved by the initial license.
  - Weak network copyleft: Redistribution of the software or work, modified or not, can only be made available to users interacting with your application remotely through a computer network under the initial license, but new components can be added under other licenses, see proprietary license.

**FOSS:**  
FOSS is the official definition of the Free Software Foundation or the Open Source Initiative.
Possible values are:
  - We consider it is FOSS
  - We consider it is NOT FOSS
  - FOSS - deduced (when it's approved by the FSF or the OSI)
  - NOT FOSS - deduced (when the FSF or the OSI have explicitly declared it as such)

**Permissive:** 
When the open source license does not require redistribution/reuse of the component under the terms of the same agreement.

**Law choice:**  
Provision of the License Agreement establishing the law applicable to the License Agreement.

**Venue choice:**  
Provision of the License Agreement establishing the location of competent courts in case of litigation relating to the License Agreement.

**Disclaimer of Warranty:**  
A provision in the License Agreement aiming at excluding or limiting certain warranties over the said component.

**Limitation of Liability:**  
Provision in the contract that reduces or eliminates the possibility of being held liable for an event related to a product or service offered

**Full Clause**	
Full clause	Indicates whether the no warranty and limitation of liability clause is fulfilled.

**AND:** 
Term indicating that the right holder has submitted the component to multiple licenses at once

**OR:**
Term that indicates that the owner of the right to subject the component to multiple licenses from which the user can choose 

### Foss Policy 

**Review status**  
The possible choices are:
- To check
- Checked
- To discuss
- Pending

**FOSS Policy status**  
The status of the license as defined by the Open Source policy. 

Possible choices are:
- Always allowed (Green)
- Never allowed (Red)
- Allowed depending on the context (Orange)

Note: the Policy will remain Grey until it has been reviewed


### Conditions of use

**Patent grant**  
A specific situation in which the text of a license also grants an exclusive, worldwide license on the patents to make, have made, use and sell the licensed products.
**Patent Peace:**
Enforcing patents against licensees or making a non-infringement agreement contrary to the license is prohibited.

**Ethical clause**  
 A provision in the License Agreement setting certain rules relating to ethical practices and laws that may apply.

**Only non-commercial use**  
Provision in the contract prohibiting its use is subject to a financial consideration or a commercial advantage.

### Specific technical notions

**Dependencies:**
Software element necessary for the execution of a program. A distinction is made between direct dependencies (dependencies that are called explicitly by the application that uses them) and indirect dependencies (called "dependencies of dependencies" of the application).
**Network access:** 
Functionalities provided by the network (back-end).
**Non-source code distribution:** 
Distribution in a form (e.g. binaries/object code/obfuscated code, etc.) which is not the preferred form for carrying out modifications.
**Source code Distribution:** 
Distribution in a preferred form for making changes (source code).
**Source code and non source code distribution:** 
Distribution  in a preferred form for making changes (source code) and in a form (e.g. binaries/object code/obfuscated code, etc.) which is not the preferred form for carrying out modifications.
**To normalize:**	
Check that components have valid SPDX license expressions during the Step 1 and add curation if not.
**Versions:**	
Versions refer to components (release refer to a product).

### Other optional information

The information below can be useful, but is considered secondary from an operational point of view (only available in the Django Admin interface).

- **categories:** 
- **steward:** 
- **osi_approved:** 
- **fsf_approved:** 
- **non_tivoisation:** 

## Authorized contexts and specific derogations

For licenses that are allowed only in certain contexts, it is possible to define them automatically if they only depend on technical criteria:
- The type of linking between the dependency and your own code
- The type of exploitation that will be made of the dependency : the exploitation mode is how the software component is shared with a) third parties or b) inside a company.
- The modification status of the dependency
- The scope in which the dependency is used
- A category to which the product belongs: a category makes it possible to group together several products sharing a common characteristic that makes sense at the company level. 

**An authorized context** is context in which a license is authorized according to technical or business criteria. 

**A specific derogation** allow the use of a license that is not authorized a priori in the context of a specific project or component. They are granted on a case-by-case basis by the company's ad hoc entity, justified, etc.

## Obligations and compliance actions

### License obligations

**Core obligation:** 
Set of obligations an organization systematically applies according to its open source compliance policy. 
**Core status:** 
Status indicating whether or not the obligation is in the core.

#### Text of the obligations

For each license that you analyze, you can extract from its text the part that is relevant to each individual obligation.
For instance, in the BSD-3-Clause, this would be typed :

>  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

#### Active/Passive obligation

**Active Obligations**
Active obligations are those that require the team to act.


For instance, in the BSD-3-Clause, the following obligation is active:

> 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

**Passive Obligations**

Passive obligations are those that can be met without specific action.

For instance, in the BSD-3-Clause, the following obligation is passive:

>  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#### Triggers of the obligation

An active obligation can be triggered by the combination of two factors. The first one is related to the exploitation of the software, the second one to its modification status. 

- **Exploitation**: 
  - Distribution as source code
  - Distribution as non source form
  - Providing access through the network  

If an obligation is triggered by two different types of exploitation, you'll have to create two instances of this obligation, one for each triggering scenario.

- **Modification**: 
Indicates if the obligations apply only if the component is modified, only if it is not modified or in both cases.

### Compliance actions

A licence obligation can be related to a compliance action (in older versions of Hermine, a "generic obligation"). A compliance action is a way to group license obligations that would amount to the same operational actions.

### Core set of compliance actions

Some compliance actions are very common and have a low cost of implementations. It often appears more effective to honor for every license, even if the license doesn't explicitly require it.  

The set of such compliance actions are named "core compliance actions".

So if a release of a product has all its compliance actions in the core, you know that you don't have any specific action to perform to reach compliance.


