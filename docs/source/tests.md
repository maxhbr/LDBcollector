<!---  
SPDX-FileCopyrightText: 2022 Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Tests

Hermine uses [Django's default test framework](https://docs.djangoproject.com/en/4.1/topics/testing/overview/), 
unittest.


## Running the tests

To run the existing tests: 

```bash
cd hermine
python manage.py test
```

## Coverage

To calculate the coverage of the existing tests:

```bash
coverage run manage.py test
coverage html
```

This will create a `htmlcov/index.html` report that you can read in your browser.


