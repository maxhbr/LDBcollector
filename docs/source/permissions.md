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

* `cube.view_release` gives access to a release summary, SBOM (view and export), validation state and obligations.
* `cube.change_release` allows to change the release details and exploitation mode.
*  the special permissions `cube.change_release_bom` is used for uploading releases SBOM.
* `cube.view_*`, `cube.add_*`, and `cube.change_*` are used for other views.

## Groups

The following groups are created by default:

* Project manager 
* Legal 
* Compliance officer 
* Guest 


The "Admin" profile is not a group per but a `user.is_staff` attribute.

(See [the Django migration](https://gitlab.com/hermine-project/hermine/-/blob/main/hermine/cube/migrations/0040_default_groups.py?ref_type=heads) for details)
