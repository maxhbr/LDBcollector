# Alias Decisions

This page keeps track of alias decisions we did for LicenseLynx when we discovered ambiguity.

## GNU Licenses: `-or-later` as the Default (Issue [#75](https://github.com/licenselynx/licenselynx/issues/75))

Ambiguous GNU license aliases that don't encode `-only` or `-or-later` are mapped to the `-or-later` variant on
the [risky map](risky-mappings.md).

### Rule

For aliases like `gpl-2.0`, `GPLv2`, `GPL v2`, `GNU General Public License v2`, we place them into the `-or-later` files but in the risky list.

Also, ScanCode LicenseDB placed the aliases without the suffix to `-only`, which we decide is wrong.
To prevent the re-importing these aliases in future auto-updates, we put them into the `rejected` list. 

Exceptions kept on the **stable** map as exact matches:

| Alias (exact) | Resolves to        | Reason                                                  |
|---------------|--------------------|---------------------------------------------------------|
| `GPL-2.0`     | `GPL-2.0-only`     | Deprecated SPDX ID, explicitly `-only` per SPDX history |
| `GPL-2.0+`    | `GPL-2.0-or-later` | Deprecated SPDX ID, explicitly `-or-later`              |

The same pattern applies to every `<family>-<version>` / `<family>-<version>+` deprecated SPDX ID.

### Reasoning

The FSF's guidance on identifying GNU
licenses ([gnu.org/licenses/identify-licenses-clearly](https://www.gnu.org/licenses/identify-licenses-clearly.html)) notes that the GNU
licenses have always permitted upgrading to later versions unless explicitly restricted, and that bare version references should be read
as "or later" by default. Mapping ambiguous strings to `-or-later` matches the upstream intent.

We also contacted Richard Stallman and asked him for this opinion and his answer was following quote:

>  **Richard Stallman's answer**
> 
> I suggest you urge them to make it unambiguous.


### Scope

Applies to all GNU license families with `-only` / `-or-later` variants:

- GPL 1.0, 2.0, 3.0
- LGPL 2.0, 2.1, 3.0
- AGPL 1.0, 3.0
- GFDL 1.1, 1.2, 1.3

### PyPI Classifiers

PyPI trove classifiers like `License :: OSI Approved :: GNU General Public License v2 (GPLv2)` encode no `-only`/`-or-later` distinction and
are treated similar to the other aliases, i.e. mapped to `-or-later` on the risky map.
