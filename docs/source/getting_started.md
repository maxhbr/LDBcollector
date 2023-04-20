<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->


# Getting started

## Main concepts used

- In Hermine a ***product*** is a piece of software that you develop internally.
- ***Procucts*** can be grouped into differents ***categories***.
- A ***release*** is a version of a product.
- A ***component*** is a third party FOSS component used by you 
- A ***version*** is a version of a component
- A ***scope*** is a scenario in which a 3rd party dependency is used. Typically, in a nodeJS project there is two scopes: `dependencies` and `devDependencies`. 
The exact meaning depends on each package manager (see for instance [Maven's documentation for Dependency Scopes](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html#Dependency_Scope))


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
to list the most frequently used Open Source component accross all your products, etc.

## Manual workflow

### Define a licence policy by reviewing licences 

You must first create a licence policy by [analysing the Open Source licences](defining_a_FOSS_policy.md).
If you want to test the application, you can import the shared data provided by the Hermine project (analysed licences and generic obligations) :
- Download the [Generic obligations JSON file](https://gitlab.com/hermine-project/hermine/-/blob/main/examples/data/Example_generic_obligations.json) and import it from the <span class ="guilabel">Generic Obligations</span> page. 
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

There are currently two supported formats to import raw SBOMS: [OSS Review Toolkit]'s native format and SPDX.

#### OSS Review Toolkit's EvaluatedModel 

- To generate an `EvaluatedModel` report with ORT from the Analyzer results:

```bash
ort analyze -i /path/to/sourcecode -o /folder/for/analyzer/ -f JSON
```
then

```bash
ort report -f EvaluatedModel -i /folder/for/analyzer/analyzer-result.json -o /folder/for/reporter  
```
#### SPDX

SPDX support is still basic at the moment. Exports from Artifactory or Fossology seem to work, but further testing is still needed.

#### Importing

To import the raw SBOM, go to the "Import components" tab, and select:
- your format (cf. supra) and the location of the file
- If you want to delete the current content of the release or not
- And the type of linking, between the dependencies listed in this import and the code base of your product.


### Validate your import

Go to the "Validation steps" tab to validate the components you have just imported.

#### Validation Step 1

Check that all the packages have a proper SPDX expression.

Some package may miss licence information or carry information that doesn't follow the SPDX standard.

You can create "curation" rules. That will be stored and reused when the same component is used in another release/product.

#### Validation Step 2

Confirm ANDs operators in SPDX expressions are not actual mis-reported ORs.

In some situations multiple licences are just expressed as a list, which is automatically converted as a cumulative expression ("A AND B"), while the reality of the licencing is actually alternative ("A OR B"), often causing false alarms.

#### Validation Step 3

This will list every scope used in you release and check that every one of them has an exploitation mode defined.

#### Validation Step 4

When a component is proposed under different licences, you must explicitely which one will be applied in your situation. You can create choice rules that will apply to different component / versions.

#### Validation Step 5

Check that the licences are compatible with your policy.
You can add derogations in order to handle specific cases.

### Read your validated SBOM

Once you have passed all the validation steps, you can read the resulting SBOM in the "Bill of Materials" tab. You can tweak each usage, for instance to change the exploitation on individual components. 

### Read your obligations

The "Obligations" tab lists the resulting obligations.





