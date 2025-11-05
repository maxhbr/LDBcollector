<!---
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr>
SPDX-License-Identifier: CC-BY-4.0
-->


# Getting started

## Main concepts used

- In Hermine a ***product*** is a piece of software that you develop internally.
- ***Products*** can be grouped into different ***categories***.
- A ***release*** is a version of a product.
- A ***component*** is a third party FOSS component used by you
- A ***version*** is a version of a component
- A ***scope*** is a scenario in which a 3rd party dependency is used. Typically, in a nodeJS project there are two scopes: `dependencies` and `devDependencies`.
The exact meaning depends on each package manager (see for instance [Maven's documentation for Dependency Scopes](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html#Dependency_Scope))

Definitions of various terms related to compliance have been collected in [a glossary (ODS format)](_static/Hermine_glossary.ods).

## Main questions Hermine helps you answer


### Can I use a given Open Source component in my product?

Hermine helps you automatically validate the inclusion of an Open Source component in your software product.

```{image} img/Hermine_schema_validation.png
:alt: Hermine_schema_validation
:class: bg-primary
:width: 400px
:align: center
```

### What actions should I perform to comply with the licenses of the included Open Source component?

 Hermine helps you identify Which obligations you should comply with, once you have included an Open Source component in your software product.

```{image} img/Hermine_schema_obligations.png
:alt: Hermine_schema_obligations
:class: bg-primary
:width: 600px
:align: center
```

### What are the Open Source components used across my different products?

Hermine allows you to identify the different products including a given version of an Open Source component,
to list the most frequently used Open Source component across all your products, etc.

## Manual workflow

### Define a license policy by reviewing licenses

You must first create a license policy by [analyzing the Open Source licenses](defining_a_FOSS_policy.md).
If you want to test the application, you can import the shared data provided by the Hermine project (analyzed licenses and compliance actions) :
- Download the [Compliance actions JSON file](https://gitlab.com/hermine-project/hermine/-/blob/main/examples/data/Example_generic_obligations.json) and import it from the <span class ="guilabel">Generic Obligations</span> page.
- Download the [License JSON file](https://gitlab.com/hermine-project/hermine/-/blob/main/examples/data/Exemple_licences.json) and import it from the <span class ="guilabel">Licenses</span> page.


### Create product and a release

- From the Product list page (<span class ="guilabel">Your products --> All products</span>), create a new product by clicking "Create a new product"
- Then from the page of the product you've just created, create a release for this product by clicking "Create a release for this product"

### Express your exploitation choices

- The *exploitation* of a third party component is to describe what will be done with it.

It can be :
- Distribution under a source and/or non source form
- Exposing is functionalities through the network
- Internal usage only

You can define general exploitation rules for each scope of your release.

http://127.0.0.1:8080/release/1/exploitation


### Import your raw SBOM

To import the raw SBOM, go to the "Import components" tab.

#### Choose your format

There are currently four supported formats to import raw SBOMS:
- [OSS Review Toolkit](https://github.com/oss-review-toolkit/ort)'s EvaluatedModel native format
- SPDX via [spdx-tools](https://pypi.org/project/spdx-tools/)
- CycloneDX via [cyclonedx-python-lib](https://pypi.org/project/cyclonedx-python-lib/)
- Hermine variant of the [KissBom format](https://github.com/kissbom/kissbom-spec)

##### OSS Review Toolkit's EvaluatedModel

- To generate an `EvaluatedModel` report with ORT from the Analyzer results:

```bash
ort analyze -i /path/to/sourcecode -o /folder/for/analyzer/ -f JSON
```
then

```bash
ort report -f EvaluatedModel -i /folder/for/analyzer/analyzer-result.json -o /folder/for/reporter
```
##### SPDX

SPDX import relies on [spdx-tools](https://pypi.org/project/spdx-tools/). It doesn't handle scope at the moment. Beware that some export don't respect the semantic of the specification: especially, Github will export _version ranges_ instead of versions.

##### CycloneDX

CycloneDX import relies on [cyclonedx-python-lib](https://pypi.org/project/cyclonedx-python-lib/).


##### Hermine KissBom variant

This is a very simple JSON format inspired by NexB's [KissBom format](https://github.com/kissbom/kissbom-spec), and makes it easy to generate SBOMs with scope information. The only mandatory field is `purl`, which must be a [valid PURL string](https://ecma-tc54.github.io/ECMA-xxx-PURL/).

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "purl": {
        "type": "string"
      },
      "license": {
        "type": "string"
      },
      "description": {
        "type": "string"
      },
      "homepage_url": {
        "type": "string"
      },
      "funding": {
        "type": "string"
      },
      "copyright_info": {
        "type": "string"
      },
      "scope": {
        "type": "string"
      },
      "subproject": {
        "type": "string"
      },
      "linking": {
        "enum": ["Aggregation", "Dynamic","Static","Mingled"]
      },
      "component_modified": {
        "enum": ["Altered", "Unmodified"]
      }
    },
    "required": [
      "purl"
    ]
  }
}
```

#### Choose your options

Indepently of the import format, you can choose :

- If you want to delete the current content of the release before adding components to it ;
- The component update mode: if you want to overwrite existing information, or only add new ones.
- The type of linking, between the dependencies listed in this import and the code base of your product.
- The default names for the subproject and scope for the components of this import

### Validate your import

Go to the "Validation steps" tab to validate the components you have just imported. It presents 6 sub-tabs, one for each step.

#### Validation Step 1: proper license information

Check that all the packages have a proper SPDX expression.

Some package may miss license information or carry information that doesn't follow the SPDX standard.

You can create "curation" rules. That will be stored and reused when the same component is used in another release/product.

#### Validation Step 2: double checking expressions containing "AND"s

Confirm ANDs operators in SPDX expressions are not actual mis-reported ORs.

In some situations multiple licenses are just expressed as a list, which is automatically converted as a cumulative expression ("A AND B"), while the reality of the licensing is actually alternative ("A OR B"), often causing false alarms.

#### Validation Step 3: define exploitation modes

This will list every subproject/scope used in you release and check that every one of them has an "exploitation mode" defined. This is important as this will determine which obligations are triggered.

#### Validation Step 4: resolve license choices

When a component is proposed under different licenses, you must explicitly which one will be applied in your situation. You can create choice rules that will apply to different component / versions.

#### Validation Step 5: check compatibility with your policy

Check that the licenses are compatible with your policy.
You can add derogations in order to handle specific corner cases.

### Read your validated SBOM

Once you have passed all the validation steps, you can read the resulting SBOM in the "Bill of Materials" tab. You can tweak each usage, for instance to change the exploitation on individual components. You can also export the result as CSV.

### Read your obligations

The "Obligations" tab lists the resulting obligations.
