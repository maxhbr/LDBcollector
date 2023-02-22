<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Permissions

Django generates a set of permissions for each model. All permissions are prefixed with `cube.`.
For example, for the `Product` model, the following permissions are generated:
* `cube.add_product`
* `cube.change_product`
* `cube.delete_product`
* `cube.view_product`

Hermine only uses a subset of these permissions to control access to the different
views, but you can still use them if you want fine control over the access to the admin.

## Permissions used by Hermine

Hermine uses permissions according to the following rules:

*  the special permissions `cube.change_release_sbom` is used for uploading releases SBOM.
* `cube.view_release` gives access to a release summary, SBOM (view and export), validation state and obligations.
* `cube.view_*`, `cube.add_*`, and `cube.change_*` are used for other views.

## Groups

The following groups are created by default:

TODO
