Creative Commons Attribution Non Commercial Share Alike 2.0 Generic (CC-BY-NC-SA-2.0)
=====================================================================================

[TABLE]

Comments on (easy) usability
----------------------------

-   **↓**“Google Classification is CANNOT\_BE\_USED "Everything that
    Google undertakes, including research, is considered a commercial
    endeavor, so no code released under a license that restricts it to
    non-commercial uses may be used at Google. For example, works under
    any Creative Commons licenses containing NC (CC BY-NC, CC BY-NC-SA,
    CC BY-NC-ND) may not be used at Google."” (source: [Google OSS
    Policy](https://opensource.google.com/docs/thirdparty/licenses/ "Google OSS Policy")
    ([CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode "CC-BY-4.0")))

-   **↓**“This license is not compatible with the
    DebianFreeSoftwareGuidelines (DFSG-unfree)” (source: [Debian Free
    Software
    Guidelines](https://wiki.debian.org/DFSGLicenses "Debian Free Software Guidelines")
    (NOASSERTION))

General Comments
----------------

URLs
----

-   **SPDX:** http://spdx.org/licenses/CC-BY-NC-SA-2.0.json

-   https://creativecommons.org/licenses/by-nc-sa/2.0/legalcode

------------------------------------------------------------------------

Raw Data
--------

### Facts

-   LicenseName

-   Override

-   [Debian Free Software
    Guidelines](https://wiki.debian.org/DFSGLicenses "Debian Free Software Guidelines")
    (NOASSERTION)

-   [Google OSS
    Policy](https://opensource.google.com/docs/thirdparty/licenses/ "Google OSS Policy")
    ([CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode "CC-BY-4.0"))

-   [SPDX](https://spdx.org/licenses/CC-BY-NC-SA-2.0.html "SPDX") (all
    data \[in this repository\] is generated)

### Raw JSON

    {
        "__impliedNames": [
            "CC-BY-NC-SA-2.0",
            "Creative Commons Attribution Non Commercial Share Alike 2.0 Generic"
        ],
        "__impliedId": "CC-BY-NC-SA-2.0",
        "__impliedAmbiguousNames": [
            "Creative Commons Attribution-Non Commercial-Share Alike (CC-by-nc-sa)"
        ],
        "__impliedRatingState": [
            [
                "Override",
                {
                    "tag": "FinalRating",
                    "contents": {
                        "tag": "RNoGo"
                    }
                }
            ]
        ],
        "__impliedNonCommercial": true,
        "facts": {
            "LicenseName": {
                "implications": {
                    "__impliedNames": [
                        "CC-BY-NC-SA-2.0"
                    ],
                    "__impliedId": "CC-BY-NC-SA-2.0"
                },
                "shortname": "CC-BY-NC-SA-2.0",
                "otherNames": []
            },
            "SPDX": {
                "isSPDXLicenseDeprecated": false,
                "spdxFullName": "Creative Commons Attribution Non Commercial Share Alike 2.0 Generic",
                "spdxDetailsURL": "http://spdx.org/licenses/CC-BY-NC-SA-2.0.json",
                "_sourceURL": "https://spdx.org/licenses/CC-BY-NC-SA-2.0.html",
                "spdxLicIsOSIApproved": false,
                "spdxSeeAlso": [
                    "https://creativecommons.org/licenses/by-nc-sa/2.0/legalcode"
                ],
                "_implications": {
                    "__impliedNames": [
                        "CC-BY-NC-SA-2.0",
                        "Creative Commons Attribution Non Commercial Share Alike 2.0 Generic"
                    ],
                    "__impliedId": "CC-BY-NC-SA-2.0",
                    "__isOsiApproved": false,
                    "__impliedURLs": [
                        [
                            "SPDX",
                            "http://spdx.org/licenses/CC-BY-NC-SA-2.0.json"
                        ],
                        [
                            null,
                            "https://creativecommons.org/licenses/by-nc-sa/2.0/legalcode"
                        ]
                    ]
                },
                "spdxLicenseId": "CC-BY-NC-SA-2.0"
            },
            "Debian Free Software Guidelines": {
                "LicenseName": "Creative Commons Attribution-Non Commercial-Share Alike (CC-by-nc-sa)",
                "State": "DFSGInCompatible",
                "_sourceURL": "https://wiki.debian.org/DFSGLicenses",
                "_implications": {
                    "__impliedNames": [
                        "CC-BY-NC-SA-2.0"
                    ],
                    "__impliedAmbiguousNames": [
                        "Creative Commons Attribution-Non Commercial-Share Alike (CC-by-nc-sa)"
                    ],
                    "__impliedJudgement": [
                        [
                            "Debian Free Software Guidelines",
                            {
                                "tag": "NegativeJudgement",
                                "contents": "This license is not compatible with the DebianFreeSoftwareGuidelines (DFSG-unfree)"
                            }
                        ]
                    ]
                },
                "Comment": null,
                "LicenseId": "CC-BY-NC-SA-2.0"
            },
            "Override": {
                "oNonCommecrial": true,
                "implications": {
                    "__impliedNames": [
                        "CC-BY-NC-SA-2.0"
                    ],
                    "__impliedId": "CC-BY-NC-SA-2.0",
                    "__impliedRatingState": [
                        [
                            "Override",
                            {
                                "tag": "FinalRating",
                                "contents": {
                                    "tag": "RNoGo"
                                }
                            }
                        ]
                    ],
                    "__impliedNonCommercial": true
                },
                "oName": "CC-BY-NC-SA-2.0",
                "oOtherLicenseIds": [],
                "oDescription": null,
                "oJudgement": null,
                "oCompatibilities": null,
                "oRatingState": {
                    "tag": "FinalRating",
                    "contents": {
                        "tag": "RNoGo"
                    }
                }
            },
            "Google OSS Policy": {
                "rating": "CANNOT_BE_USED",
                "_sourceURL": "https://opensource.google.com/docs/thirdparty/licenses/",
                "id": "CC-BY-NC-SA-2.0",
                "_implications": {
                    "__impliedNames": [
                        "CC-BY-NC-SA-2.0"
                    ],
                    "__impliedJudgement": [
                        [
                            "Google OSS Policy",
                            {
                                "tag": "NegativeJudgement",
                                "contents": "Google Classification is CANNOT_BE_USED \"Everything that Google undertakes, including research, is considered a commercial endeavor, so no code released under a license that restricts it to non-commercial uses may be used at Google. For example, works under any Creative Commons licenses containing NC (CC BY-NC, CC BY-NC-SA, CC BY-NC-ND) may not be used at Google.\""
                            }
                        ]
                    ]
                },
                "description": "Everything that Google undertakes, including research, is considered a commercial endeavor, so no code released under a license that restricts it to non-commercial uses may be used at Google. For example, works under any Creative Commons licenses containing NC (CC BY-NC, CC BY-NC-SA, CC BY-NC-ND) may not be used at Google."
            }
        },
        "__impliedJudgement": [
            [
                "Debian Free Software Guidelines",
                {
                    "tag": "NegativeJudgement",
                    "contents": "This license is not compatible with the DebianFreeSoftwareGuidelines (DFSG-unfree)"
                }
            ],
            [
                "Google OSS Policy",
                {
                    "tag": "NegativeJudgement",
                    "contents": "Google Classification is CANNOT_BE_USED \"Everything that Google undertakes, including research, is considered a commercial endeavor, so no code released under a license that restricts it to non-commercial uses may be used at Google. For example, works under any Creative Commons licenses containing NC (CC BY-NC, CC BY-NC-SA, CC BY-NC-ND) may not be used at Google.\""
                }
            ]
        ],
        "__isOsiApproved": false,
        "__impliedURLs": [
            [
                "SPDX",
                "http://spdx.org/licenses/CC-BY-NC-SA-2.0.json"
            ],
            [
                null,
                "https://creativecommons.org/licenses/by-nc-sa/2.0/legalcode"
            ]
        ]
    }

### Dot Cluster Graph

[../dot/CC-BY-NC-SA-2.0.svg](../dot/CC-BY-NC-SA-2.0.svg "../dot/CC-BY-NC-SA-2.0.svg")
