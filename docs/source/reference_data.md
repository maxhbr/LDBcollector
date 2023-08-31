<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Reference data

You can import reference data in Hermine. This data is a
collection of licenses and generic obligations. Once you
have loaded reference data into Hermine, you can compare
your local licenses and obligations to the reference ones,
and if you want, update you local values to match the
reference.

It is meant to share legal knowledge between Hermine users, 
without sharing any confidential information. It is also 
meant to be a starting point for your own policy, and you 
can edit it to fit your needs.

Reference data is a JSON file with the following keys :
* `date` : the date of the reference data
* `version` : the version of the reference data
* `objects` : a list of licenses, obligations and generic
  obligations in [Django serialization format](https://docs.djangoproject.com/en/4.2/topics/serialization/)

You should obtain your reference data file from a
third party, so generating this file is outside the scope
of this documentation.

## Importing reference data

Because reference data is cached at runtime, you will have
to restart your server after importing reference data. 

```bash
# in your poetry environment
python hermine/manage.py init_reference_data path/to/reference_data.json
```
