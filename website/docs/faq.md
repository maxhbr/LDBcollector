# Frequently Asked Questions

## How does LicenseLynx find the canonical name?

What a canonical name of a license depends on the definition.
LicenseLynx doesn't decide that a certain license name has this certain canonical name.
As a primary source the SPDX license list is used because it is widely accepted.

For licenses with no SPDX entry, ScanCode LicenseDB is the next source where their key is used as the canonical name.
To follow where the canonical name comes from, each license file has a field ``src``, so other users know the source of the information.
Also, the ``aliases`` entry is a JSON Object where each key is the source and each value is a list with the aliases.

The canonical names can change, e.g. if SPDX adds licenses to its list and therefor LicenseLynx will change the canonical name.
But at least LicenseLynx provides a base with deterministic strings which we can work with.

## What is the difference to projects like FOSSology?

LicenseLynx solely focuses on mapping licenses with their canonical name and providing these mappings as libraries in different programming languages.
With these libraries other tools can use the mappings for license identification.
FOSSology has a different angle on license compliance and aims to solve it at once whereas LicenseLynx plays a part in a more decentralized apporach for license compliance.

## Why is LicenseLynx not using a database?

The best database is no database.

## What if there is a error in the data?

In the case of a wrong mapping or even an old mapping, an Issue can be created.
For more information head to [Contributing](contribution.md).

## How to suggest changes in the data?

Contribtions for LicenseLynx are very welcome and can be done via creating Issues and merge request.
For more information head to [Contributing](contribution.md).
