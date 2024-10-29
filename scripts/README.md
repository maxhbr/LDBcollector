# Scripts for data handling, statistics, and Web API

## Introduction

These scripts manage our data.

- **Load**: Creates and updates the `merged_data.json` files, which map all aliases to their canonical names.
- **Update**: Updates the data folder from the data and also updates the statistics in the root readme file.
- **Validate**: Checks if the data files meet our [constraints](#constraints).
- **web_api**: Creates in the pipeline for the GitLab pages-job the json-files to imitate a Web API based on the directory structure.

## Constraints

### General Constraints

- **JSON Extension**: Files should have the `.json` extension.
- **Directory**: All JSON files are located in the `DATA_DIR`.

### Filename and Content Checks

#### 1. Canonical Name Check

- The JSON filename (excluding the `.json` extension) must match the `canonical` name field inside the JSON file.

#### 2. Unique Aliases Check

- Aliases within each JSON file must be globally unique across all JSON files.

#### 3. Canonical Name Check
- The canonical identifier must be the equal to canonical identifier from the source of the JSON file.

#### 4. Length and Characters Check

- **Maximum Length**: `canonical`, `aliases`, and `src` fields must not exceed 100 characters.
- **Forbidden Characters**: `canonical` name must not contain any of the following characters: `#, $, %, =, [, ], ?, <, >, :, /, \, |, *, ` ` (space)`.

#### 5. No empty fields

- Every key in the JSON file has a non-null value.
- **Exception**: the value for the key `custom` in the `aliases` object is allowed to be empty.

## Usage

To execute the different scripts, run the following commands:

``` bash
poetry run merge_data -o merged_data.json
poetry run data_validation
poetry run spdx_data_update 
poetry run scancode_licensedb_data_update
poetry run update_readme
poetry run generate_api_files
```

## Web API

The LicenseLynx Web API simulates an API environment but functions as a file directory hosted on GitLab Pages.
To maintain compatibility with this structure, any entry containing a / must be replaced with an _.
Below are the instructions for making this replacement in both Windows and Linux systems for bash and PowerShell if the modification should be done programmatically.

The API call format is: ``/api/license/{license_name}.json``

It is also possible to retrieve the whole license mapping as one json-file.
The URL is ``/json/{version}/mapping.json``. 
The version number is necessary due to modifications and additions of licenses over time.
To always get the most recent version, use ``/json/latest/mapping.json``.

## Options

The script ``merge_data.py`` has one option, ```--output/-o```, where the output path and file name are specified.
The file must end with ```.json```.

The script ``generate_api_files.py`` has two options.
First option is ``--input/-i``, which takes the merged data file from ``merge_data.py``.
Second option is ``--dir/-d``, which is by default ``api/license`` and creates the files for the Web API.
