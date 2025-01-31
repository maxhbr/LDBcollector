# Frequently Asked Questions

## How does LicenseLynx find the canonical name?

What a canonical name of a license is depends on the definition.
LicenseLynx doesn't decide that a certain license name has a specific canonical name.  
As a primary source, the SPDX license list is used because it is widely accepted.

For licenses with no SPDX entry, ScanCode LicenseDB is the next source, where their key is used as the canonical name.
To track where the canonical name comes from, each license file has a field ``src``, so other users know the source of the information.
Additionally, the ``aliases`` entry is a JSON object where each key is the source and each value is a list of aliases.

Canonical names can change, e.g., if SPDX adds licenses to its list, LicenseLynx will update the canonical name accordingly.  
However, LicenseLynx provides a base with deterministic strings that can be consistently used.

## What is the difference from projects like FOSSology?

LicenseLynx solely focuses on mapping licenses with their canonical name and providing these mappings as libraries in different programming languages.
With these libraries, other tools can use the mappings for license identification.  
FOSSology has a different approach to license compliance, aiming to solve it comprehensively, whereas LicenseLynx plays a part in a more decentralized approach to license compliance.

## Why is LicenseLynx not using a database?

For adding and editing the data, it is much simpler to use JSON files.  
We also don't have huge dependencies between different entities, but rather a collection of license files populated with canonical names and aliases.

## What if there is an error in the data?

In the case of a wrong or outdated mapping, an issue can be created.  
For more information, refer to [Contributing](contribution.md).

## How to suggest changes in the data?

Contributions to LicenseLynx are very welcome and can be done by creating issues and merge requests.  
For more information, refer to [Contributing](contribution.md).
