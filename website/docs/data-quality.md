# Data Quality

Our goal with LicenseLynx is to provide deterministic license mappings.
Therefore, we aim for 100% correct mappings without ambiguity.
That means, that the data mapping must not be **mostly correct** or **the AI says it is so**, and so on.
If we can't be sure the mapping is correct, we don't provide that mapping.

This doesn't exclude that the data is free of any errors.
But it's open and can be fixed by everyone, reviewed by us.
Data quality is already very high, but it will improve over time.

Since we automatically update the data with some external sources (e.g. the [SPDX License List](https://github.com/spdx/license-list-data/blob/main/json/licenses.json){:target="_blank"}) without review, new errors may be introduced.
We try to mitigate these with some [data validation rules](https://licenselynx.org/licenselynxworks/#data-import), but semantic errors may not be detectable by these criteria.
Those semantic errors can be found and remedied via the rejected lists.
