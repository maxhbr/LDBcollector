# Scripts for data source handling

## Introduction
These scripts manage our data source. 

- **Load**: Creates and updates the `merged_data.json` files, which map all aliases to their canonical names.
- **Update**: Updates the data source with new changes from the SPDX license list.
- **Validate**: Checks if the data source and `merged_data.json` files meet our [constraints](#constraints).


## Constraints
### General Constraints
- **JSON Extension**: Files should have the `.json` extension.
- **Directory**: All JSON files are located in the `DATASOURCE_DIR`.

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
poetry run datasource_update
poetry run merge_datasource -o merged_data.json
poetry run datasource_validation
```

## Options

The script ``merge_datasource.py`` has one option, ```--output/-o```, where the output path and file name are specified.
The file must end with ```.json```.
