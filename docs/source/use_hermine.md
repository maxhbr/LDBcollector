<!---  
SPDX-FileCopyrightText: 2022 Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Using Hermine

Hermine is an Open Source tool meant to complement existing ones in the field of Open Source legal compliance.
It serves to main purposes: managing your SBOMs (Software Bill of Materials) and helping you analyzing Open Source licences in order to automatically apply these analyses to your SBOMs.


## Getting started

### Main concepts used

- In Hermine a "product" is a piece of software that you develop internally.
- A "release" is a version of a product.
- A "component" is a thrid party FOSS component used by you 
- A "version" is a version of a component

### Manual workflow

You can use Hermine through the GUI

#### Import your raw SBOM

- Create a product and a release for this product in Django's admin
- Generate an export from ORT

```
ort analyze -i /path/to/sourcecode -o /folder/for/analyzer/ -f JSON
```

then

```
ort report -f EvaluatedModel -i /folder/for/analyzer/analyzer-result.json -o /folder/for/reporter  
```
- Import the report at http://127.0.0.1:8080/import/bom 

#### Validate your import

http://127.0.0.1:8080/release/1

- Step 1 Check that all the packages have a proper SPDX expression 
- Step 2 Check that all the licences involved have been analyzed by your legal departement
- Step 3 Express your choices when several licences are proposed
- Step 4 Check that the licences are compatible with your policy

#### Express your exploitation choices

http://127.0.0.1:8080/release/1/exploitation


#### Read your obligations

http://127.0.0.1:8080/release/24/obligations



