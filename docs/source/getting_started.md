<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->


# Getting started

## Main concepts used

- In Hermine a "product" is a piece of software that you develop internally.
- A "release" is a version of a product.
- A "component" is a third party FOSS component used by you 
- A "version" is a version of a component

## Manual workflow

You can use Hermine through the GUI for one shot analysis

### Import your raw SBOM

- Create a product and a release for this product in Django's admin
- Generate an `EvaluatedModel` report with ORT from the Analyzer results:

```bash
ort analyze -i /path/to/sourcecode -o /folder/for/analyzer/ -f JSON
```

then

```bash
ort report -f EvaluatedModel -i /folder/for/analyzer/analyzer-result.json -o /folder/for/reporter  
```
- Import the report at http://127.0.0.1:8080/release/1/bom/

Where '1' is the id for the release you're working on.

### Express your exploitation choices

http://127.0.0.1:8080/release/1/exploitation

### Validate your import

http://127.0.0.1:8080/release/1

#### Validation Step 1
Checks that all the packages have a proper SPDX expression.
Some package may miss licence information or carry information that doesn't follow 
the SPDX standard.

#### Validation Step 2
Checks that all the licenses involved have been analyzed by your legal departement

#### Validation Step 3
Confirm ANDs operators in SPDX expressions are not poorly registered ORs.
In some situations multiple licences are just expressed as a list, which is 
automatically converted as a cumulative expression ("A AND B"), while the reality of the 
licencing is actually alternative ("A OR B"), causing often false alarms.

#### Validation Step 4 
Express your choices when several licenses are proposed.


#### Validation Step 5
Check that the licenses are compatible with your policy.
You can add derogations in order to handle specific cases.

### Read your validated SBOM


### Read your obligations

http://127.0.0.1:8080/release/1/obligations



