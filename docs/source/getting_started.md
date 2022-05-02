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
- Generate an export from ORT

```bash
ort analyze -i /path/to/sourcecode -o /folder/for/analyzer/ -f JSON
```

then

```bash
ort report -f EvaluatedModel -i /folder/for/analyzer/analyzer-result.json -o /folder/for/reporter  
```
- Import the report at http://127.0.0.1:8080/import/bom 

### Express your exploitation choices

http://127.0.0.1:8080/release/1/exploitation

### Validate your import

http://127.0.0.1:8080/release/1

#### Validation Step 1
Check that all the packages have a proper SPDX expression 

#### Validation Step 2
Check that all the licences involved have been analyzed by your legal departement

#### Validation Step 3
Confirm ANDs operators in SPDX expressions are not poorly registered ORs.

#### Validation Step 4 
Express your choices when several licences are proposed.

#### Validation Step 5
Check that the licences are compatible with your policy.

### Read your obligations

http://127.0.0.1:8080/release/1/obligations



