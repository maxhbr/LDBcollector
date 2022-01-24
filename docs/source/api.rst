.. SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
..
.. SPDX-License-Identifier: CC-BY-4.0

API
========
Hermine is a Free software under license `AGPL-3.0-only <https://www.gnu.org/licenses/agpl-3.0>`_.


Authentication through API
---------------------------------

Authentication is handled through a Token system.
Make a POST request on 'api/token-auth/' with the fields 'username' and 'password' in a form-data.
THis will give you a response like 


.. code-block:: json

    {
        "token": "1273e3f6XXXXXXXXXXXXXXXX71209ac3bf29"
    }

Then, you can make any API call with this token given in a HTTP Header 
"Authorization" : "Token 1273e3f6XXXXXXXXXXXXXXXX71209ac3bf29".

Note : there must be a white space between Token and the token itself.

In a python requests in would look like 


.. code-block:: python
    
    import requests

    url = 'http://127.0.0.1:8080/releases/'
    headers = {'Authorization': 'Token 1273e3f6XXXXXXXXXXXXXXXX71209ac3bf29'}
    r = requests.get(url, headers=headers)


API endpoints for Models
---------------------------------

API endpoint for each class is accessible through '/api/<str:class_name>'. 

A detail view for an instance of a class can be found at '/api/<str:class_name>/<int:instance_id>'.

More information about API endpoints parameters can be found in the Views page.


Upload of SPDX file 
---------------------------------

Can be found at '/api/upload_spdx/'.

While properly authenticated, you are allowed to POST a SPDX.yaml file to a chosen release. Fill the following in form-data:

* spdx_file : the file you want to upload. It should be a YAML file that comes from an ORT digest.
* release_id :  the integer identifying the release you aim at


Validation steps
---------------------------------

The validation process of a release is divided in 4 steps. You need to complete them in the right order.

When you encounter a result that does not fit requirements to go to next step, you'll need to make the appropriate work inside Hermine UI.

Every endpoint has a "valid" field that is set to True if every action that should be done has been done, and False otherwise.


Step 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Can be found at 'api/releases/<int:release_id>/validation-1/'

API endpoint that allows to know if there are Unnormalised Usages.

The response is a dictionnary with the following fields :

unnormalised_usages
    An array of usage objects for which no license expression has been expressed.
 

Step 2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Can be found at 'api/releases/<int:release_id>/validation-2/'

API endpoint that allows to know if there are Licenses that have not been checked by the legal team so far. 

The response is a dictionnary with the following fields :

licenses_to_check
    An array of license objects that are considered as "grey" and therefore need a manual check.

licenses_to_create
    An array of licenses that need to be created in hermine's database.


Step 3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Can be found at 'api/releases/<int:release_id>/validation-3/'

API endpoint that allows to know if there are complex license expressions in usages of this release.

A complex license expression is an expression with more than one License expressed in it.

A choice has to be made, either by keeping the whole expression either by picking the chosen licenses in the expression.

The response is a dictionnary with the following fields :

to_resolve
    An array of usages linked to a version that either has a complex "corrected_license" eother a "spdx_valid_license_expr" field, and for which no explicit choice as been made.
    To make a choice, click on "choose expression" in hermine UI. Pick the desired scope, type the actual expression you'll want to use for this component, and enter an explanation for your choice.
    This will create a UsageChoice object that is linked to the Usage object.

resolved
    An array of usages linked to a version hat either has a complex "corrected_license" eother a "spdx_valid_license_expr" field, and for which an explicit choice as been made.


Step 4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Can be found at 'api/releases/<int:release_id>/validation-4/'
API endpoint that allows to know if there are Usages of unnacepted licenes in this release.
In this case, you must set relevant derogations in Hermine UI.

The response is a dictionnary with the following fields :

usages_lic_red
    An array of usages containing a license that has been marked as "red" by the legal team.

usages_lic_orange
    An array of usages containing a license that has been marked as "orange" by the legal team, which means that this license can sometimes be accepted depending on the context.

usages_lic_grey
    An array of usages containing a license that still has to be reviewed by the legal team.

involved_lic
    An array containing all the licenses that are red, orange or grey and that need a derogation for this release.

derogations
    An array of the derogations that has been made.
