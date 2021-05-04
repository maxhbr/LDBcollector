GNU General Public License v1.0 or later (GPL-1.0-or-later)
===========================================================

[TABLE]

**Other Names:**

-   `GPL-1.0+`

-   `GPL1.0+`

-   `GPL1+`

Comments on (easy) usability
----------------------------

-   **↑**“This is the most popular free software license. Most of Linux
    (the kernel) is distributed under the GPL, as is most of the other
    basic software in the GNU operating system.” (source: [Debian Free
    Software
    Guidelines](https://wiki.debian.org/DFSGLicenses "Debian Free Software Guidelines")
    (NOASSERTION))

-   **↑**“This software Licenses is OK for Fedora” (source: [Fedora
    Project
    Wiki](https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing "Fedora Project Wiki")
    ([CC-BY-SA-3.0](https://creativecommons.org/licenses/by-sa/3.0/legalcode "CC-BY-SA-3.0")))

-   **↓**“Google Classification is RESTRICTED” (source: [Google OSS
    Policy](https://opensource.google.com/docs/thirdparty/licenses/ "Google OSS Policy")
    ([CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode "CC-BY-4.0")))

General Comments
----------------

URLs
----

-   **SPDX:** http://spdx.org/licenses/GPL-1.0-or-later.json

-   https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html

------------------------------------------------------------------------

Raw Data
--------

### Facts

-   LicenseName

-   Override

-   [Debian Free Software
    Guidelines](https://wiki.debian.org/DFSGLicenses "Debian Free Software Guidelines")
    (NOASSERTION)

-   [Fedora Project
    Wiki](https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing "Fedora Project Wiki")
    ([CC-BY-SA-3.0](https://creativecommons.org/licenses/by-sa/3.0/legalcode "CC-BY-SA-3.0"))

-   [Google OSS
    Policy](https://opensource.google.com/docs/thirdparty/licenses/ "Google OSS Policy")
    ([CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode "CC-BY-4.0"))

-   [librariesio
    license-compatibility](https://github.com/librariesio/license-compatibility/blob/master/lib/license/licenses.json "librariesio license-compatibility")
    ([MIT](https://github.com/librariesio/license-compatibility/blob/master/LICENSE.txt "MIT"))

-   [SPDX](https://spdx.org/licenses/GPL-1.0-or-later.html "SPDX") (all
    data \[in this repository\] is generated)

### Raw JSON

    {
        "__impliedNames": [
            "GPL-1.0-or-later",
            "GPL-1.0+",
            "GPL1.0+",
            "GPL1+",
            "GNU General Public License v1.0 or later"
        ],
        "__impliedId": "GPL-1.0-or-later",
        "__isFsfFree": true,
        "__impliedAmbiguousNames": [
            "The GNU General Public License (GPL)",
            "GPL+"
        ],
        "facts": {
            "LicenseName": {
                "implications": {
                    "__impliedNames": [
                        "GPL-1.0-or-later"
                    ],
                    "__impliedId": "GPL-1.0-or-later"
                },
                "shortname": "GPL-1.0-or-later",
                "otherNames": []
            },
            "SPDX": {
                "isSPDXLicenseDeprecated": false,
                "spdxFullName": "GNU General Public License v1.0 or later",
                "spdxDetailsURL": "http://spdx.org/licenses/GPL-1.0-or-later.json",
                "_sourceURL": "https://spdx.org/licenses/GPL-1.0-or-later.html",
                "spdxLicIsOSIApproved": false,
                "spdxSeeAlso": [
                    "https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html"
                ],
                "_implications": {
                    "__impliedNames": [
                        "GPL-1.0-or-later",
                        "GNU General Public License v1.0 or later"
                    ],
                    "__impliedId": "GPL-1.0-or-later",
                    "__isOsiApproved": false,
                    "__impliedURLs": [
                        [
                            "SPDX",
                            "http://spdx.org/licenses/GPL-1.0-or-later.json"
                        ],
                        [
                            null,
                            "https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html"
                        ]
                    ]
                },
                "spdxLicenseId": "GPL-1.0-or-later"
            },
            "librariesio license-compatibility": {
                "implications": {
                    "__impliedNames": [
                        "GPL-1.0-or-later"
                    ],
                    "__impliedCopyleft": [
                        [
                            "librariesio license-compatibility",
                            "StrongCopyleft"
                        ]
                    ],
                    "__calculatedCopyleft": "StrongCopyleft"
                },
                "licensename": "GPL-1.0-or-later",
                "copyleftkind": "StrongCopyleft"
            },
            "Fedora Project Wiki": {
                "GPLv2 Compat?": "Yes",
                "rating": "Good",
                "Upstream URL": "Note that this is not GPLv1+, because 1+ is the same as any version.",
                "GPLv3 Compat?": "Yes",
                "Short Name": "GPL+",
                "licenseType": "license",
                "_sourceURL": "https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing",
                "Full Name": "GNU General Public License v1.0 or later",
                "FSF Free?": "Yes",
                "_implications": {
                    "__impliedNames": [
                        "GNU General Public License v1.0 or later"
                    ],
                    "__isFsfFree": true,
                    "__impliedAmbiguousNames": [
                        "GPL+"
                    ],
                    "__impliedJudgement": [
                        [
                            "Fedora Project Wiki",
                            {
                                "tag": "PositiveJudgement",
                                "contents": "This software Licenses is OK for Fedora"
                            }
                        ]
                    ]
                }
            },
            "Debian Free Software Guidelines": {
                "LicenseName": "The GNU General Public License (GPL)",
                "State": "DFSGCompatible",
                "_sourceURL": "https://wiki.debian.org/DFSGLicenses",
                "_implications": {
                    "__impliedNames": [
                        "GPL-1.0-or-later"
                    ],
                    "__impliedAmbiguousNames": [
                        "The GNU General Public License (GPL)"
                    ],
                    "__impliedJudgement": [
                        [
                            "Debian Free Software Guidelines",
                            {
                                "tag": "PositiveJudgement",
                                "contents": "This is the most popular free software license. Most of Linux (the kernel) is distributed under the GPL, as is most of the other basic software in the GNU operating system."
                            }
                        ]
                    ]
                },
                "Comment": "This is the most popular free software license. Most of Linux (the kernel) is distributed under the GPL, as is most of the other basic software in the GNU operating system.",
                "LicenseId": "GPL-1.0-or-later"
            },
            "Override": {
                "oNonCommecrial": null,
                "implications": {
                    "__impliedNames": [
                        "GPL-1.0-or-later",
                        "GPL-1.0+",
                        "GPL1.0+",
                        "GPL1+"
                    ],
                    "__impliedId": "GPL-1.0-or-later"
                },
                "oName": "GPL-1.0-or-later",
                "oOtherLicenseIds": [
                    "GPL-1.0+",
                    "GPL1.0+",
                    "GPL1+"
                ],
                "oDescription": null,
                "oJudgement": null,
                "oCompatibilities": null,
                "oRatingState": null
            },
            "Google OSS Policy": {
                "rating": "RESTRICTED",
                "_sourceURL": "https://opensource.google.com/docs/thirdparty/licenses/",
                "id": "GPL-1.0-or-later",
                "_implications": {
                    "__impliedNames": [
                        "GPL-1.0-or-later"
                    ],
                    "__impliedJudgement": [
                        [
                            "Google OSS Policy",
                            {
                                "tag": "NegativeJudgement",
                                "contents": "Google Classification is RESTRICTED"
                            }
                        ]
                    ]
                }
            }
        },
        "__impliedJudgement": [
            [
                "Debian Free Software Guidelines",
                {
                    "tag": "PositiveJudgement",
                    "contents": "This is the most popular free software license. Most of Linux (the kernel) is distributed under the GPL, as is most of the other basic software in the GNU operating system."
                }
            ],
            [
                "Fedora Project Wiki",
                {
                    "tag": "PositiveJudgement",
                    "contents": "This software Licenses is OK for Fedora"
                }
            ],
            [
                "Google OSS Policy",
                {
                    "tag": "NegativeJudgement",
                    "contents": "Google Classification is RESTRICTED"
                }
            ]
        ],
        "__impliedCopyleft": [
            [
                "librariesio license-compatibility",
                "StrongCopyleft"
            ]
        ],
        "__calculatedCopyleft": "StrongCopyleft",
        "__isOsiApproved": false,
        "__impliedURLs": [
            [
                "SPDX",
                "http://spdx.org/licenses/GPL-1.0-or-later.json"
            ],
            [
                null,
                "https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html"
            ]
        ]
    }

### Dot Cluster Graph

[../dot/GPL-1.0-or-later.svg](../dot/GPL-1.0-or-later.svg "../dot/GPL-1.0-or-later.svg")
