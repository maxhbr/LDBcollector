# OSS License Open Data

**NOTE: This is in draft status. The schema and contents are subject to change.**

Open data of logically decomposed OSS licenses.

## Description

We publish the logically decomposed OSS licenses as open data in order to make it easy for people to understand OSS licenses. We believe it contributes to development of OSS.

Each license is decomposed into vocabularies for actions, conditions, and notices. Conditions construct logic tree with AND node, OR node, and LEAF node. This is the reason we call this data as "logically decomposed" OSS licenses.

## Data format

The data is distributed in an exchange format using JSON as following files:

* [licenses.json](data/licenses.json) - Logically decomposed OSS Licenses which consist of actions, conditions, and notices.
* [actions.json](data/actions.json) - Vocabularies for actions.
* [conditions.json](data/conditions.json) - Vocabularies for conditions.
* [notices.json](data/notices.json) - Vocabularies for notices.

### common attributes

Metadata:

| attribute | description |
| --- | --- |
| data | Top of each element |
| schemaVersion | Version of schema. This documentation is for 0.1  |
| uri | URI to identify the data |
| baseUri | Base for relative URI in the "ref" attribute |
| id | ID of the data. It shoud correspond to uri |

Structure of language specific attributes:

```javascript
"(attribute name)": [
  {
    "language": "(language subtag *1)"
    "text": "(attribute value)"
  }
]
```
(*1) e.g. "en", "ja". see [RFC5646](https://tools.ietf.org/html/rfc5646)

### licenses.json

Structure:

```text
data
  (metadata)
  spdx
  summary
  description
  permissions
    summary
    description
    actions
    conditionHead
  notices
  content
```

| attribute | description |
| --- | --- |
| name | Name of the license |
| spdx | SPDX identifier (optional) |
| summary | Summary of the license (language specific) |
| description | Description of the license (language specific) |
| content | License text |

Permissions sub structure:

| attribute | description |
| --- | --- |
| permissions | List of actions and conditions. The conditions must be fulfilled when the action is taken |
| summary | Summary of the permission (language specific) |
| description | Description of the permission (language specific) |

Actions sub structure:

| attribute | description |
| --- | --- |
| actions | List of references to actions |
| ref | Reference to an action |

Logic tree sub structure:

| attribute | description |
| --- | --- |
| conditionHead | Reference to head of logic tree of conditions |
| type | Type of the logic tree node. The value is one of "AND", "OR", "LEAF" |
| children | Children of "AND" or "OR" node |
| ref | Reference to a condition for "LEAF" node |

Notices sub structure:

| attribute | description |
| --- | --- |
| notices | List of references to notices |
| ref | Reference to a notice |

### actions.json

Structure:

```text
data
  (metadata)
  name
  description
```

| attribute | description |
| --- | --- |
| name | Name of the action (language specific) |
| description | Description of the action (language specific) |

### conditions.json

Structure:

```text
data
  (metadata)
  conditionType
  name
  description
```

| attribute | description |
| --- | --- |
| conditionType | Type of the condition. The value is one of following: <ul><li>"OBLIGATION" - must be fulfilled when actions are taken</li><li>"RESTRICTION" - must be fulfilled after actions are taken</li><li>"REQUISITE" - must be fulfilled before actions are taken</li></ul> |
| name | Name of the condition (language specific) |
| description | Description of the condition (language specific) |

### notices.json

Structure:

```text
data
  (metadata)
  content
  description
```

| attribute | description |
| --- | --- |
| content | Content of the notice (language specific) |
| description | Description of the notice (language specific) |

## License

The open data is licensed under Community Data License Agreement Permissive 1.0. The data is provided on an "AS IS" bases without any warranties. See [LICENSE.pdf](LICENSE.pdf) for details.

SPDX-License-Identifier: CDLA-Permissive-1.0
