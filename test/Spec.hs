{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes #-}

import qualified Prelude as P
import           MyPrelude

import           Test.Hspec
import           Test.QuickCheck
import           Control.Exception (evaluate)
import Text.RawString.QQ

import           Debug.Trace (trace)

import           Data.Either
import           Data.Text (Text)
import qualified Data.Vector as V
import           Data.Vector (Vector)
import qualified Data.ByteString.Char8 as Char8

import qualified Data.Aeson.Lens as AL

import           Lib


facts :: Facts
facts = let
  f1 = mkLicenseFullnameFact "MIT" "MIT License"
  f2 = mkLicenseFullnameFact "BSD-3-Clause" "BSD-3-Clause License"
  f3 = mkLicenseFullnameFact "GPL-2.0-or-later" "GNU General Public License v2.0 or later"
  t1 = mkLicenseTextFact "MIT" "MIT Text..."
  t2 = mkLicenseTextFact "BSD-3-Clause" "BSD-3-Clause Text..."
  t3 = mkLicenseTextFact "GPL-2.0+" "Text for: GNU General Public License v2.0 or later"
  in V.fromList [f1, f2, f3, t1, t2, t3]

spdxExample = [r|{
  "licenseListVersion": "3.5-1-g1266c6b",
  "licenses": [
    {
      "reference": "./0BSD.html",
      "isDeprecatedLicenseId": false,
      "detailsUrl": "http://spdx.org/licenses/0BSD.json",
      "referenceNumber": "315",
      "name": "BSD Zero Clause License",
      "licenseId": "0BSD",
      "seeAlso": [
        "http://landley.net/toybox/license.html"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./AAL.html",
      "isDeprecatedLicenseId": false,
      "detailsUrl": "http://spdx.org/licenses/AAL.json",
      "referenceNumber": "21",
      "name": "Attribution Assurance License",
      "licenseId": "AAL",
      "seeAlso": [
        "https://opensource.org/licenses/attribution"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./ADSL.html",
      "isDeprecatedLicenseId": false,
      "detailsUrl": "http://spdx.org/licenses/ADSL.json",
      "referenceNumber": "19",
      "name": "Amazon Digital Services License",
      "licenseId": "ADSL",
      "seeAlso": [
        "https://fedoraproject.org/wiki/Licensing/AmazonDigitalServicesLicense"
      ],
      "isOsiApproved": false
    },
    {
      "reference": "./AFL-1.1.html",
      "isDeprecatedLicenseId": false,
      "isFsfLibre": true,
      "detailsUrl": "http://spdx.org/licenses/AFL-1.1.json",
      "referenceNumber": "115",
      "name": "Academic Free License v1.1",
      "licenseId": "AFL-1.1",
      "seeAlso": [
        "http://opensource.linux-mirror.org/licenses/afl-1.1.txt",
        "http://wayback.archive.org/web/20021004124254/http://www.opensource.org/licenses/academic.php"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./AFL-1.2.html",
      "isDeprecatedLicenseId": false,
      "isFsfLibre": true,
      "detailsUrl": "http://spdx.org/licenses/AFL-1.2.json",
      "referenceNumber": "133",
      "name": "Academic Free License v1.2",
      "licenseId": "AFL-1.2",
      "seeAlso": [
        "http://opensource.linux-mirror.org/licenses/afl-1.2.txt",
        "http://wayback.archive.org/web/20021204204652/http://www.opensource.org/licenses/academic.php"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./AFL-2.0.html",
      "isDeprecatedLicenseId": false,
      "isFsfLibre": true,
      "detailsUrl": "http://spdx.org/licenses/AFL-2.0.json",
      "referenceNumber": "112",
      "name": "Academic Free License v2.0",
      "licenseId": "AFL-2.0",
      "seeAlso": [
        "http://wayback.archive.org/web/20060924134533/http://www.opensource.org/licenses/afl-2.0.txt"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./AFL-2.1.html",
      "isDeprecatedLicenseId": false,
      "isFsfLibre": true,
      "detailsUrl": "http://spdx.org/licenses/AFL-2.1.json",
      "referenceNumber": "248",
      "name": "Academic Free License v2.1",
      "licenseId": "AFL-2.1",
      "seeAlso": [
        "http://opensource.linux-mirror.org/licenses/afl-2.1.txt"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./AFL-3.0.html",
      "isDeprecatedLicenseId": false,
      "isFsfLibre": true,
      "detailsUrl": "http://spdx.org/licenses/AFL-3.0.json",
      "referenceNumber": "213",
      "name": "Academic Free License v3.0",
      "licenseId": "AFL-3.0",
      "seeAlso": [
        "http://www.rosenlaw.com/AFL3.0.htm",
        "https://opensource.org/licenses/afl-3.0"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./AGPL-1.0.html",
      "isDeprecatedLicenseId": true,
      "isFsfLibre": true,
      "detailsUrl": "http://spdx.org/licenses/AGPL-1.0.json",
      "referenceNumber": "330",
      "name": "Affero General Public License v1.0",
      "licenseId": "AGPL-1.0",
      "seeAlso": [
        "http://www.affero.org/oagpl.html"
      ],
      "isOsiApproved": false
    },
    {
      "reference": "./AGPL-1.0-only.html",
      "isDeprecatedLicenseId": false,
      "detailsUrl": "http://spdx.org/licenses/AGPL-1.0-only.json",
      "referenceNumber": "376",
      "name": "Affero General Public License v1.0 only",
      "licenseId": "AGPL-1.0-only",
      "seeAlso": [
        "http://www.affero.org/oagpl.html"
      ],
      "isOsiApproved": false
    },
    {
      "reference": "./AGPL-1.0-or-later.html",
      "isDeprecatedLicenseId": false,
      "detailsUrl": "http://spdx.org/licenses/AGPL-1.0-or-later.json",
      "referenceNumber": "327",
      "name": "Affero General Public License v1.0 or later",
      "licenseId": "AGPL-1.0-or-later",
      "seeAlso": [
        "http://www.affero.org/oagpl.html"
      ],
      "isOsiApproved": false
    },
    {
      "reference": "./AGPL-3.0.html",
      "isDeprecatedLicenseId": true,
      "isFsfLibre": true,
      "detailsUrl": "http://spdx.org/licenses/AGPL-3.0.json",
      "referenceNumber": "226",
      "name": "GNU Affero General Public License v3.0",
      "licenseId": "AGPL-3.0",
      "seeAlso": [
        "https://www.gnu.org/licenses/agpl.txt",
        "https://opensource.org/licenses/AGPL-3.0"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./AGPL-3.0-only.html",
      "isDeprecatedLicenseId": false,
      "isFsfLibre": true,
      "detailsUrl": "http://spdx.org/licenses/AGPL-3.0-only.json",
      "referenceNumber": "92",
      "name": "GNU Affero General Public License v3.0 only",
      "licenseId": "AGPL-3.0-only",
      "seeAlso": [
        "https://www.gnu.org/licenses/agpl.txt",
        "https://opensource.org/licenses/AGPL-3.0"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./AGPL-3.0-or-later.html",
      "isDeprecatedLicenseId": false,
      "isFsfLibre": true,
      "detailsUrl": "http://spdx.org/licenses/AGPL-3.0-or-later.json",
      "referenceNumber": "152",
      "name": "GNU Affero General Public License v3.0 or later",
      "licenseId": "AGPL-3.0-or-later",
      "seeAlso": [
        "https://www.gnu.org/licenses/agpl.txt",
        "https://opensource.org/licenses/AGPL-3.0"
      ],
      "isOsiApproved": true
    },
    {
      "reference": "./AMDPLPA.html",
      "isDeprecatedLicenseId": false,
      "detailsUrl": "http://spdx.org/licenses/AMDPLPA.json",
      "referenceNumber": "32",
      "name": "AMD\u0027s plpa_map.c License",
      "licenseId": "AMDPLPA",
      "seeAlso": [
        "https://fedoraproject.org/wiki/Licensing/AMD_plpa_map_License"
      ],
      "isOsiApproved": false
    },
    {
      "reference": "./AML.html",
      "isDeprecatedLicenseId": false,
      "detailsUrl": "http://spdx.org/licenses/AML.json",
      "referenceNumber": "145",
      "name": "Apple MIT License",
      "licenseId": "AML",
      "seeAlso": [
        "https://fedoraproject.org/wiki/Licensing/Apple_MIT_License"
      ],
      "isOsiApproved": false
    }
  ],
  "releaseDate": "2019-04-02"
}|]

blueOakExample = [r|{
  "version": "1",
  "ratings": [
    {
      "name": "Model",
      "licenses": [
        {
          "name": "Blue Oak Model License 1.0.0",
          "id": "BlueOak-1.0.0",
          "url": "https://blueoakcouncil.org/license/1.0.0"
        }
      ]
    },
    {
      "name": "Gold",
      "licenses": [
        {
          "name": "BSD-2-Clause Plus Patent License",
          "id": "BSD-2-Clause-Patent",
          "url": "https://spdx.org/licenses/BSD-2-Clause-Patent.html"
        }
      ]
    },
    {
      "name": "Silver",
      "licenses": [
        {
          "name": "Amazon Digital Services License",
          "id": "ADSL",
          "url": "https://spdx.org/licenses/ADSL.html"
        },
        {
          "name": "Apache License 2.0",
          "id": "Apache-2.0",
          "url": "https://spdx.org/licenses/Apache-2.0.html"
        },
        {
          "name": "Adobe Postscript AFM License",
          "id": "APAFML",
          "url": "https://spdx.org/licenses/APAFML.html"
        },
        {
          "name": "BSD 1-Clause License",
          "id": "BSD-1-Clause",
          "url": "https://spdx.org/licenses/BSD-1-Clause.html"
        },
        {
          "name": "BSD 2-Clause \"Simplified\" License",
          "id": "BSD-2-Clause",
          "url": "https://spdx.org/licenses/BSD-2-Clause.html"
        },
        {
          "name": "BSD 2-Clause FreeBSD License",
          "id": "BSD-2-Clause-FreeBSD",
          "url": "https://spdx.org/licenses/BSD-2-Clause-FreeBSD.html"
        },
        {
          "name": "BSD 2-Clause NetBSD License",
          "id": "BSD-2-Clause-NetBSD",
          "url": "https://spdx.org/licenses/BSD-2-Clause-NetBSD.html"
        },
        {
          "name": "Boost Software License 1.0",
          "id": "BSL-1.0",
          "url": "https://spdx.org/licenses/BSL-1.0.html"
        },
        {
          "name": "DSDP License",
          "id": "DSDP",
          "url": "https://spdx.org/licenses/DSDP.html"
        },
        {
          "name": "Educational Community License v1.0",
          "id": "ECL-1.0",
          "url": "https://spdx.org/licenses/ECL-1.0.html"
        },
        {
          "name": "Educational Community License v2.0",
          "id": "ECL-2.0",
          "url": "https://spdx.org/licenses/ECL-2.0.html"
        },
        {
          "name": "ImageMagick License",
          "id": "ImageMagick",
          "url": "https://spdx.org/licenses/ImageMagick.html"
        },
        {
          "name": "ISC License",
          "id": "ISC",
          "url": "https://spdx.org/licenses/ISC.html"
        },
        {
          "name": "Linux Kernel Variant of OpenIB.org license",
          "id": "Linux-OpenIB",
          "url": "https://spdx.org/licenses/Linux-OpenIB.html"
        },
        {
          "name": "MIT License",
          "id": "MIT",
          "url": "https://spdx.org/licenses/MIT.html"
        },
        {
          "name": "Microsoft Public License",
          "id": "MS-PL",
          "url": "https://spdx.org/licenses/MS-PL.html"
        },
        {
          "name": "Mup License",
          "id": "Mup",
          "url": "https://spdx.org/licenses/Mup.html"
        },
        {
          "name": "PostgreSQL License",
          "id": "PostgreSQL",
          "url": "https://spdx.org/licenses/PostgreSQL.html"
        },
        {
          "name": "Spencer License 99",
          "id": "Spencer-99",
          "url": "https://spdx.org/licenses/Spencer-99.html"
        },
        {
          "name": "Universal Permissive License v1.0",
          "id": "UPL-1.0",
          "url": "https://spdx.org/licenses/UPL-1.0.html"
        },
        {
          "name": "Xerox License",
          "id": "Xerox",
          "url": "https://spdx.org/licenses/Xerox.html"
        }
      ]
    },
    {
      "name": "Bronze",
      "licenses": [
        {
          "id": "0BSD",
          "url": "https://spdx.org/licenses/0BSD.html",
          "name": "BSD Zero Clause License"
        },
        {
          "id": "AFL-1.1",
          "url": "https://spdx.org/licenses/AFL-1.1.html",
          "name": "Academic Free License v1.1"
        },
        {
          "id": "AFL-1.2",
          "url": "https://spdx.org/licenses/AFL-1.2.html",
          "name": "Academic Free License v1.2"
        },
        {
          "id": "AFL-2.0",
          "url": "https://spdx.org/licenses/AFL-2.0.html",
          "name": "Academic Free License v2.0"
        },
        {
          "id": "AFL-2.1",
          "url": "https://spdx.org/licenses/AFL-2.1.html",
          "name": "Academic Free License v2.1"
        },
        {
          "id": "AFL-3.0",
          "url": "https://spdx.org/licenses/AFL-3.0.html",
          "name": "Academic Free License v3.0"
        },
        {
          "id": "AMDPLPA",
          "url": "https://spdx.org/licenses/AMDPLPA.html",
          "name": "AMD's plpa_map.c License"
        },
        {
          "id": "AML",
          "url": "https://spdx.org/licenses/AML.html",
          "name": "Apple MIT License"
        },
        {
          "id": "AMPAS",
          "url": "https://spdx.org/licenses/AMPAS.html",
          "name": "Academy of Motion Picture Arts and Sciences BSD"
        },
        {
          "id": "ANTLR-PD",
          "url": "https://spdx.org/licenses/ANTLR-PD.html",
          "name": "ANTLR Software Rights Notice"
        },
        {
          "id": "Apache-1.0",
          "url": "https://spdx.org/licenses/Apache-1.0.html",
          "name": "Apache License 1.0"
        },
        {
          "id": "Apache-1.1",
          "url": "https://spdx.org/licenses/Apache-1.1.html",
          "name": "Apache License 1.1"
        },
        {
          "id": "Artistic-2.0",
          "url": "https://spdx.org/licenses/Artistic-2.0.html",
          "name": "Artistic License 2.0"
        },
        {
          "id": "Bahyph",
          "url": "https://spdx.org/licenses/Bahyph",
          "name": "Bahyph License"
        },
        {
          "id": "Barr",
          "url": "https://spdx.org/licenses/Barr.html",
          "name": "Barr License"
        },
        {
          "id": "BSD-3-Clause",
          "url": "https://spdx.org/licenses/BSD-3-Clause.html",
          "name": "BSD 3-Clause \"New\" or \"Revised\" License"
        },
        {
          "id": "BSD-3-Clause-Attribution",
          "url": "https://spdx.org/licenses/BSD-3-Clause-Attribution.html",
          "name": "BSD with attribution"
        },
        {
          "id": "BSD-3-Clause-Clear",
          "url": "https://spdx.org/licenses/BSD-3-Clause-Clear.html",
          "name": "BSD 3-Clause Clear License"
        },
        {
          "id": "BSD-3-Clause-LBNL",
          "url": "https://spdx.org/licenses/BSD-3-Clause-LBNL.html",
          "name": "Lawrence Berkeley National Labs BSD variant license"
        },
        {
          "id": "BSD-3-Clause-No-Nuclear-License-2014",
          "url": "https://spdx.org/licenses/BSD-3-Clause-No-Nuclear-License-2014.html",
          "name": "BSD 3-Clause No Nuclear License 2014"
        },
        {
          "id": "BSD-3-Clause-No-Nuclear-Warranty",
          "url": "https://spdx.org/licenses/BSD-3-Clause-No-Nuclear-Warranty.html",
          "name": "BSD 3-Clause No Nuclear Warranty"
        },
        {
          "id": "BSD-4-Clause",
          "url": "https://spdx.org/licenses/BSD-4-Clause.html",
          "name": "BSD 4-Clause \"Original\" or \"Old\" License"
        },
        {
          "id": "BSD-4-Clause-UC",
          "url": "https://spdx.org/licenses/BSD-4-Clause-UC.html",
          "name": "BSD-4-Clause (University of California-Specific)"
        },
        {
          "id": "BSD-Source-Code",
          "url": "https://spdx.org/licenses/BSD-Source-Code.html",
          "name": "BSD Source Code Attribution"
        },
        {
          "id": "bzip2-1.0.5",
          "url": "https://spdx.org/licenses/bzip2-1.0.5.html",
          "name": "bzip2 and libbzip2 License v1.0.5"
        },
        {
          "id": "bzip2-1.0.6",
          "url": "https://spdx.org/licenses/bzip2-1.0.6.html",
          "name": "bzip2 and libbzip2 License v1.0.6"
        },
        {
          "id": "CC0-1.0",
          "url": "https://spdx.org/licenses/CC0-1.0.html",
          "name": "Creative Commons Zero v1.0 Universal"
        },
        {
          "id": "CNRI-Jython",
          "url": "https://spdx.org/licenses/CNRI-Jython.html",
          "name": "CNRI Jython License"
        },
        {
          "id": "CNRI-Python",
          "url": "https://spdx.org/licenses/CNRI-Python.html",
          "name": "CNRI Python License"
        },
        {
          "id": "CNRI-Python-GPL-Compatible",
          "url": "https://spdx.org/licenses/CNRI-Python-GPL-Compatible.html",
          "name": "CNRI Python Open Source GPL Compatible License Agreement"
        },
        {
          "id": "Cube",
          "url": "https://spdx.org/licenses/Cube.html",
          "name": "Cube License"
        },
        {
          "id": "curl",
          "url": "https://spdx.org/licenses/curl.html",
          "name": "curl License"
        },
        {
          "id": "eGenix",
          "url": "https://spdx.org/licenses/eGenix.html",
          "name": "eGenix.com Public License 1.1.0"
        },
        {
          "id": "Entessa",
          "url": "https://spdx.org/licenses/Entessa.html",
          "name": "Entessa Public License v1.0"
        },
        {
          "id": "FTL",
          "url": "https://spdx.org/licenses/FTL.html",
          "name": "Freetype Project License"
        },
        {
          "id": "IBM-pibs",
          "url": "https://spdx.org/licenses/IBM-pibs.html",
          "name": "IBM PowerPC Initialization and Boot Software"
        },
        {
          "id": "ICU",
          "url": "https://spdx.org/licenses/ICU.html",
          "name": "ICU License"
        },
        {
          "id": "Info-ZIP",
          "url": "https://spdx.org/licenses/Info-ZIP.html",
          "name": "Info-ZIP License"
        },
        {
          "id": "Intel",
          "url": "https://spdx.org/licenses/Intel.html",
          "name": "Intel Open Source License"
        },
        {
          "id": "JasPer-2.0",
          "url": "https://spdx.org/licenses/JasPer-2.0.html",
          "name": "JasPer License"
        },
        {
          "id": "Libpng",
          "url": "https://spdx.org/licenses/Libpng.html",
          "name": "libpng License"
        },
        {
          "id": "libtiff",
          "url": "https://spdx.org/licenses/libtiff.html",
          "name": "libtiff License"
        },
        {
          "id": "LPPL-1.3c",
          "url": "https://spdx.org/licenses/LPPL-1.3c.html",
          "name": "LaTeX Project Public License v1.3c"
        },
        {
          "id": "MIT-0",
          "url": "https://spdx.org/licenses/MIT-0.html",
          "name": "MIT No Attribution"
        },
        {
          "id": "MIT-advertising",
          "url": "https://spdx.org/licenses/MIT-advertising.html",
          "name": "Enlightenment License (e16)"
        },
        {
          "id": "MIT-CMU",
          "url": "https://spdx.org/licenses/MIT-CMU.html",
          "name": "CMU License"
        },
        {
          "id": "MIT-enna",
          "url": "https://spdx.org/licenses/MIT-enna.html",
          "name": "enna License"
        },
        {
          "id": "MIT-feh",
          "url": "https://spdx.org/licenses/MIT-feh.html",
          "name": "feh License"
        },
        {
          "id": "MITNFA",
          "url": "https://spdx.org/licenses/MITNFA.html",
          "name": "MIT +no-false-attribs license"
        },
        {
          "id": "MTLL",
          "url": "https://spdx.org/licenses/MTLL.html",
          "name": "Matrix Template Library License"
        },
        {
          "id": "Multics",
          "url": "https://spdx.org/licenses/Multics.html",
          "name": "Multics License"
        },
        {
          "id": "Naumen",
          "url": "https://spdx.org/licenses/Naumen.html",
          "name": "Naumen Public License"
        },
        {
          "id": "NCSA",
          "url": "https://spdx.org/licenses/NCSA.html",
          "name": "University of Illinois/NCSA Open Source License"
        },
        {
          "id": "Net-SNMP",
          "url": "https://spdx.org/licenses/Net-SNMP.html",
          "name": "Net-SNMP License"
        },
        {
          "id": "NetCDF",
          "url": "https://spdx.org/licenses/NetCDF.html",
          "name": "NetCDF license"
        },
        {
          "id": "NTP",
          "url": "https://spdx.org/licenses/NTP.html",
          "name": "NTP License"
        },
        {
          "id": "OLDAP-2.0",
          "url": "https://spdx.org/licenses/OLDAP-2.0.html",
          "name": "Open LDAP Public License v2.0 (or possibly 2.0A and 2.0B)"
        },
        {
          "id": "OLDAP-2.0.1",
          "url": "https://spdx.org/licenses/OLDAP-2.0.1.html",
          "name": "Open LDAP Public License v2.0.1"
        },
        {
          "id": "OLDAP-2.1",
          "url": "https://spdx.org/licenses/OLDAP-2.1.html",
          "name": "Open LDAP Public License v2.1"
        },
        {
          "id": "OLDAP-2.2",
          "url": "https://spdx.org/licenses/OLDAP-2.2.html",
          "name": "Open LDAP Public License v2.2"
        },
        {
          "id": "OLDAP-2.2.1",
          "url": "https://spdx.org/licenses/OLDAP-2.2.1.html",
          "name": "Open LDAP Public License v2.2.1"
        },
        {
          "id": "OLDAP-2.2.2",
          "url": "https://spdx.org/licenses/OLDAP-2.2.2.html",
          "name": "Open LDAP Public License 2.2.2"
        },
        {
          "id": "OLDAP-2.3",
          "url": "https://spdx.org/licenses/OLDAP-2.3.html",
          "name": "Open LDAP Public License v2.3"
        },
        {
          "id": "OLDAP-2.4",
          "url": "https://spdx.org/licenses/OLDAP-2.4.html",
          "name": "Open LDAP Public License v2.4"
        },
        {
          "id": "OLDAP-2.5",
          "url": "https://spdx.org/licenses/OLDAP-2.5.html",
          "name": "Open LDAP Public License v2.5"
        },
        {
          "id": "OLDAP-2.6",
          "url": "https://spdx.org/licenses/OLDAP-2.6.html",
          "name": "Open LDAP Public License v2.6"
        },
        {
          "id": "OLDAP-2.7",
          "url": "https://spdx.org/licenses/OLDAP-2.7.html",
          "name": "Open LDAP Public License v2.7"
        },
        {
          "id": "OLDAP-2.8",
          "url": "https://spdx.org/licenses/OLDAP-2.8.html",
          "name": "Open LDAP Public License v2.8"
        },
        {
          "id": "OML",
          "url": "https://spdx.org/licenses/OML.html",
          "name": "Open Market License"
        },
        {
          "id": "OpenSSL",
          "url": "https://spdx.org/licenses/OpenSSL.html",
          "name": "OpenSSL License"
        },
        {
          "id": "PHP-3.0",
          "url": "https://spdx.org/licenses/PHP-3.0.html",
          "name": "PHP License v3.0"
        },
        {
          "id": "PHP-3.01",
          "url": "https://spdx.org/licenses/PHP-3.01.html",
          "name": "PHP License v3.01"
        },
        {
          "id": "Plexus",
          "url": "https://spdx.org/licenses/Plexus.html",
          "name": "Plexus Classworlds License"
        },
        {
          "id": "Python-2.0",
          "url": "https://spdx.org/licenses/Python-2.0.html",
          "name": "Python License 2.0"
        },
        {
          "id": "Ruby",
          "url": "https://spdx.org/licenses/Ruby.html",
          "name": "Ruby License"
        },
        {
          "id": "Saxpath",
          "url": "https://spdx.org/licenses/Saxpath.html",
          "name": "Saxpath License"
        },
        {
          "id": "SGI-B-2.0",
          "url": "https://spdx.org/licenses/SGI-B-2.0.html",
          "name": "SGI Free Software License B v2.0"
        },
        {
          "id": "SMLNJ",
          "url": "https://spdx.org/licenses/SMLNJ.html",
          "name": "Standard ML of New Jersey License"
        },
        {
          "id": "SWL",
          "url": "https://spdx.org/licenses/SWL.html",
          "name": "Scheme Widget Library (SWL) Software License Agreement"
        },
        {
          "id": "TCL",
          "url": "https://spdx.org/licenses/TCL.html",
          "name": "TCL/TK License"
        },
        {
          "id": "TCP-wrappers",
          "url": "https://spdx.org/licenses/TCP-wrappers.html",
          "name": "TCP Wrappers License"
        },
        {
          "id": "Unicode-DFS-2015",
          "url": "https://spdx.org/licenses/Unicode-DFS-2015.html",
          "name": "Unicode License Agreement - Data Files and Software (2015)"
        },
        {
          "id": "Unicode-DFS-2016",
          "url": "https://spdx.org/licenses/Unicode-DFS-2016.html",
          "name": "Unicode License Agreement - Data Files and Software (2016)"
        },
        {
          "id": "Unlicense",
          "url": "https://spdx.org/licenses/Unlicense.html",
          "name": "The Unlicense"
        },
        {
          "id": "VSL-1.0",
          "url": "https://spdx.org/licenses/VSL-1.0.html",
          "name": "Vovida Software License v1.0"
        },
        {
          "id": "W3C",
          "url": "https://spdx.org/licenses/W3C.html",
          "name": "W3C Software Notice and License (2002-12-31)"
        },
        {
          "id": "X11",
          "url": "https://spdx.org/licenses/X11.html",
          "name": "X11 License"
        },
        {
          "id": "XFree86-1.1",
          "url": "https://spdx.org/licenses/XFree86-1.1.html",
          "name": "XFree86 License 1.1"
        },
        {
          "id": "Xnet",
          "url": "https://spdx.org/licenses/Xnet.html",
          "name": "X.Net License"
        },
        {
          "id": "xpp",
          "url": "https://spdx.org/licenses/xpp.html",
          "name": "XPP License"
        },
        {
          "id": "Zlib",
          "url": "https://spdx.org/licenses/Zlib.html",
          "name": "zlib License"
        },
        {
          "id": "zlib-acknowledgement",
          "url": "https://spdx.org/licenses/zlib-acknowledgement.html",
          "name": "zlib/libpng License with Acknowledgement"
        },
        {
          "id": "ZPL-2.0",
          "url": "https://spdx.org/licenses/ZPL-2.0.html",
          "name": "Zope Public License 2.0"
        },
        {
          "id": "ZPL-2.1",
          "url": "https://spdx.org/licenses/ZPL-2.1.html",
          "name": "Zope Public License 2.1"
        }
      ]
    },
    {
      "name": "Lead",
      "licenses": [
        {
          "id": "AAL",
          "url": "https://spdx.org/licenses/AAL.html",
          "name": "Attribution Assurance License"
        },
        {
          "id": "Adobe-2006",
          "url": "https://spdx.org/licenses/Adobe-2006",
          "name": "Adobe Systems Incorporated Source Code License Agreement"
        },
        {
          "id": "Afmparse",
          "url": "https://spdx.org/licenses/Afmparse.html",
          "name": "Afmparse License"
        },
        {
          "id": "Artistic-1.0",
          "url": "https://spdx.org/licenses/Artistic-1.0.html",
          "name": "Artistic License 1.0"
        },
        {
          "id": "Artistic-1.0-cl8",
          "url": "https://spdx.org/licenses/Artistic-1.0-cl8.html",
          "name": "Artistic License 1.0 w/clause 8"
        },
        {
          "id": "Artistic-1.0-Perl",
          "url": "https://spdx.org/licenses/Artistic-1.0-Perl.html",
          "name": "Artistic License 1.0 (Perl)"
        },
        {
          "id": "Beerware",
          "url": "https://spdx.org/licenses/Beerware.html",
          "name": "Beerware License"
        },
        {
          "id": "Bourceux",
          "url": "https://spdx.org/licenses/Borceux.html",
          "name": "Borceux license"
        },
        {
          "id": "CECILL-B",
          "url": "https://spdx.org/licenses/CECILL-B.html",
          "name": "CeCILL-B Free Software License Agreement"
        },
        {
          "id": "ClArtistic",
          "url": "https://spdx.org/licenses/ClArtistic.html",
          "name": "Clarified Artistic License"
        },
        {
          "id": "Condor-1.1",
          "url": "https://spdx.org/licenses/Condor-1.1.html",
          "name": "Condor Public License v1.1"
        },
        {
          "id": "Crossword",
          "url": "https://spdx.org/licenses/Crossword.html",
          "name": "Crossword License"
        },
        {
          "id": "CrystalStacker",
          "url": "https://spdx.org/licenses/CrystalStacker.html",
          "name": "CrystalStacker License"
        },
        {
          "id": "diffmark",
          "url": "https://spdx.org/licenses/diffmark.html",
          "name": "diffmark license"
        },
        {
          "id": "DOC",
          "url": "https://spdx.org/licenses/DOC.html",
          "name": "DOC License"
        },
        {
          "id": "EFL-1.0",
          "url": "https://spdx.org/licenses/EFL-1.0.html",
          "name": "Eiffel Forum License v1.0"
        },
        {
          "id": "EFL-2.0",
          "url": "https://spdx.org/licenses/EFL-2.0.html",
          "name": "Eiffel Forum License v2.0"
        },
        {
          "id": "Fair",
          "url": "https://spdx.org/licenses/Fair.html",
          "name": "Fair License"
        },
        {
          "id": "Giftware",
          "url": "https://spdx.org/licenses/Giftware.html",
          "name": "Giftware License"
        },
        {
          "id": "HPND",
          "url": "https://spdx.org/licenses/HPND.html",
          "name": "Historical Permission Notice and Disclaimer"
        },
        {
          "id": "IJG",
          "url": "https://spdx.org/licenses/IJG.html",
          "name": "Independent JPEG Group License"
        },
        {
          "id": "Leptonica",
          "url": "https://spdx.org/licenses/Leptonica.html",
          "name": "Leptonica License"
        },
        {
          "id": "LPL-1.0",
          "url": "https://spdx.org/licenses/LPL-1.0.html",
          "name": "Lucent Public License Version 1.0"
        },
        {
          "id": "LPL-1.02",
          "url": "https://spdx.org/licenses/LPL-1.0.html",
          "name": "Lucent Public License v1.02"
        },
        {
          "id": "MirOS",
          "url": "https://spdx.org/licenses/MirOS.html",
          "name": "MirOS License"
        },
        {
          "id": "mpich2",
          "url": "https://spdx.org/licenses/mpich2.html",
          "name": "mpich2 License"
        },
        {
          "id": "NASA-1.3",
          "url": "https://spdx.org/licenses/NASA-1.3.html",
          "name": "NASA Open Source Agreement 1.3"
        },
        {
          "id": "NBPL-1.0",
          "url": "https://spdx.org/licenses/NBPL-1.0.html",
          "name": "Net Boolean Public License v1"
        },
        {
          "id": "Newsletr",
          "url": "https://spdx.org/licenses/Newsletr.html",
          "name": "Newsletr License"
        },
        {
          "id": "NLPL",
          "url": "https://spdx.org/licenses/NLPL.html",
          "name": "No Limit Public License"
        },
        {
          "id": "NRL",
          "url": "https://spdx.org/licenses/NRL.html",
          "name": "NRL License"
        },
        {
          "id": "OGTSL",
          "url": "https://spdx.org/licenses/OGTSL.html",
          "name": "Open Group Test Suite License"
        },
        {
          "id": "OLDAP-1.1",
          "url": "https://spdx.org/licenses/OLDAP-1.1.html",
          "name": "Open LDAP Public License v1.1"
        },
        {
          "id": "OLDAP-1.2",
          "url": "https://spdx.org/licenses/OLDAP-1.2.html",
          "name": "Open LDAP Public License v1.2"
        },
        {
          "id": "OLDAP-1.3",
          "url": "https://spdx.org/licenses/OLDAP-1.3.html",
          "name": "Open LDAP Public License v1.3"
        },
        {
          "id": "OLDAP-1.4",
          "url": "https://spdx.org/licenses/OLDAP-1.4.html",
          "name": "Open LDAP Public License v1.4"
        },
        {
          "id": "psutils",
          "url": "https://spdx.org/licenses/psutils.html",
          "name": "psutils License"
        },
        {
          "id": "Qhull",
          "url": "https://spdx.org/licenses/Qhull.html",
          "name": "Qhull License"
        },
        {
          "id": "Rdisc",
          "url": "https://spdx.org/licenses/Rdisc.html",
          "name": "Rdisc License"
        },
        {
          "id": "RSA-MD",
          "url": "https://spdx.org/licenses/RSA-MD.html",
          "name": "RSA Message-Digest License "
        },
        {
          "id": "Spencer-86",
          "url": "https://spdx.org/licenses/Spencer-86.html",
          "name": "Spencer License 86"
        },
        {
          "id": "Spencer-94",
          "url": "https://spdx.org/licenses/Spencer-94.html",
          "name": "Spencer License 94"
        },
        {
          "id": "TU-Berlin-1.0",
          "url": "https://spdx.org/licenses/TU-Berlin-1.0.html",
          "name": "Technische Universitaet Berlin License 1.0"
        },
        {
          "id": "TU-Berlin-2.0",
          "url": "https://spdx.org/licenses/TU-Berlin-2.0.html",
          "name": "Technische Universitaet Berlin License 2.0"
        },
        {
          "id": "W3C-19980720",
          "url": "https://spdx.org/licenses/W3C-19980720.html",
          "name": "W3C Software Notice and License (1998-07-20)"
        },
        {
          "id": "W3C-20150513",
          "url": "https://spdx.org/licenses/W3C-20150513.html",
          "name": "W3C Software Notice and Document License (2015-05-13)"
        },
        {
          "id": "Wsuipa",
          "url": "https://spdx.org/licenses/Wsuipa.html",
          "name": "Wsuipa License"
        },
        {
          "id": "WTFPL",
          "url": "https://spdx.org/licenses/WTFPL.html",
          "name": "Do What The F*ck You Want To Public License"
        },
        {
          "id": "xinetd",
          "url": "https://spdx.org/licenses/xinetd.html",
          "name": "xinetd License"
        },
        {
          "id": "Zed",
          "url": "https://spdx.org/licenses/Zed.html",
          "name": "Zed License"
        },
        {
          "id": "Zend-2.0",
          "url": "https://spdx.org/licenses/Zend-2.0.html",
          "name": "Zend License v2.0"
        },
        {
          "id": "ZPL-1.1",
          "url": "https://spdx.org/licenses/ZPL-1.1.html",
          "name": "Zope Public License 1.1"
        }
      ]
    }
  ]
}|]

blueOakMiniExample = [r|{
  "version": "1",
  "ratings": [
    {
      "name": "Gold",
      "licenses": [
        {
          "name": "BSD-2-Clause Plus Patent License",
          "id": "BSD-2-Clause-Patent",
          "url": "https://spdx.org/licenses/BSD-2-Clause-Patent.html"
        }
      ]
    },
    {
      "name": "Silver",
      "licenses": [
        {
          "name": "BSD 2-Clause \"Simplified\" License",
          "id": "BSD-2-Clause",
          "url": "https://spdx.org/licenses/BSD-2-Clause.html"
        },
        {
          "name": "MIT License",
          "id": "MIT",
          "url": "https://spdx.org/licenses/MIT.html"
        }
      ]
    }
  ]
}|]

blueOakEmptyExample = [r|{"version": "1", "ratings": []}|]

ocptExample = [r|Name,SPDX Identifier,Type,Copyleft,SaaS Deemed Distribution,Explicit Patent,Freedom or Death,Notice Requirements,Modification Requirements,Commercial Use,Provide Copy of licence ,Same licence,State Changes ,Provide Disclaimer
2-clause BSD License,BSD-2-Clause,permissive,no,no,no,no,,,yes,,,,
3-clause BSD License,BSD-3-Clause,permissive,no,no,no,no,,,yes,,,,
Academic Free License 3.0,AFL-3.0,SaaS,no,yes,yes,no,,,yes,,,,
Apache License 2.0,Apache-2.0,permissive,no,no,yes,no,,,yes,,,,
MIT License ,MIT,permissive,no,no,no,no,,,yes,,,,
|]

chooseALicenseExample = [r|permissions:
  - commercial-use
  - modifications
  - distribution
  - private-use

conditions:
  - include-copyright

limitations:
  - liability
  - warranty
|]

gnuEmptyDocument = [r|<dl class="green">
</dl> <!-- end class="green" -->
|]

gnuSingleDocument = [r|<dl class="green">

<dt><a id="GNUGPL"></a>  <!-- both generic and version-specific anchors -->
    <a id="GNUGPLv3" href="/licenses/gpl.html">
    GNU General Public License (GPL) version 3</a>
    <span class="anchor-reference-id">
      (<a href="#GNUGPL">#GNUGPL</a>)
      (<a href="#GNUGPLv3">#GNUGPLv3</a>)
    </span></dt>
<dd>
<p>This is the latest version of the GNU GPL: a free software license, and
a copyleft license.  We recommend it for most software packages.</p>

<p>Please note that GPLv3 is not compatible with GPLv2 by itself.
However, most software released under GPLv2 allows you to use the
terms of later versions of the GPL as well.  When this is the case,
you can use the code under GPLv3 to make the desired combination.  To
learn more about compatibility between GNU licenses,
please <a href="/licenses/gpl-faq.html#AllCompatibility">see our
FAQ</a>.</p></dd>

</dl> <!-- end class="green" -->
|]

gnuDoubleDocument = [r|<dl class="green">

<dt><a id="GNUGPL"></a>  <!-- both generic and version-specific anchors -->
    <a id="GNUGPLv3" href="/licenses/gpl.html">
    GNU General Public License (GPL) version 3</a>
    <span class="anchor-reference-id">
      (<a href="#GNUGPL">#GNUGPL</a>)
      (<a href="#GNUGPLv3">#GNUGPLv3</a>)
    </span></dt>
<dd>
<p>This is the latest version of the GNU GPL: a free software license, and
a copyleft license.  We recommend it for most software packages.</p>

<p>Please note that GPLv3 is not compatible with GPLv2 by itself.
However, most software released under GPLv2 allows you to use the
terms of later versions of the GPL as well.  When this is the case,
you can use the code under GPLv3 to make the desired combination.  To
learn more about compatibility between GNU licenses,
please <a href="/licenses/gpl-faq.html#AllCompatibility">see our
FAQ</a>.</p></dd>

<dt><a id="GPLv2" href="/licenses/old-licenses/gpl-2.0.html">
    GNU General Public License (GPL) version 2</a>
    <span class="anchor-reference-id">(<a href="#GPLv2">#GPLv2</a>)</span></dt>
<dd>
<p>This is the previous version of the GNU GPL: a free software license, and
a copyleft license.  We recommend <a href="#GNUGPL">the latest version</a>
for most software.</p>

<p>Please note that GPLv2 is, by itself, not compatible with GPLv3.
However, most software released under GPLv2 allows you to use the
terms of later versions of the GPL as well.  When this is the case,
you can use the code under GPLv3 to make the desired combination.  To
learn more about compatibility between GNU licenses,
please <a href="/licenses/gpl-faq.html#AllCompatibility">see our
FAQ</a>.</p></dd>

</dl> <!-- end class="green" -->
|]

main :: IO ()
main = hspec $ do
  describe "Model.License" $ let
      abc = getLicenseFromFacts "ABC" [] facts
      mit = getLicenseFromFacts "MIT" [] facts
      gpl = getLicenseFromFacts "GPL-2.0-or-later" ["GPL-2.0+"] facts
    in do
      it "there is a MIT FullnameFact" $ do
        (mit `containsFactOfType` "LicenseFullname") `shouldBe` (True :: Bool)
      it "there is no MIT FancyFact" $ do
        (mit `containsFactOfType` "FancyFact") `shouldBe` (False :: Bool)

      it "there is no ABC FullnameFact" $ do
        (abc `containsFactOfType` "LicenseFullname") `shouldBe` (False :: Bool)

      it "there is a GPL-2.0-or-later FullnameFact" $ do
        (gpl `containsFactOfType` "LicenseFullname") `shouldBe` (True :: Bool)
      it "there is a GPL-2.0-or-later TextFact" $ do
        (gpl `containsFactOfType` "LicenseText") `shouldBe` (True :: Bool)

      -- it "the MIT FullnameFact is as expected" $ do
      --   (mit `getFactData` (LFC ["LicenseFullname"])) `shouldBe` (object ["LicenseFullname" .= (toJSON ["MIT" :: String,"MIT License"] :: Value)])
      it "the ABC FullnameFact is as expected" $ do
        (abc `getFactData` (LFC ["LicenseFullname"])) `shouldBe` Nothing

  describe "Model.Query" $ do
    it "query from string" $ do
       queryByteString AL._String "\"SomeString\"" `shouldBe` Just "SomeString"
    it "query from matching json works" $ do
       queryByteString (AL.key "licenseType" . AL._String) "{\"licenseType\": \"TheType\"}" `shouldBe` Just "TheType"

  describe "Collector.SPDX" $ let
      factsFromSPDX = loadSPDXFactsFromString spdxExample
      nBSD = getLicenseFromFacts "0BSD" [] factsFromSPDX
      abc = getLicenseFromFacts "ABC" [] factsFromSPDX
    in do
      it "is possible to parse the string and gets correct count" $ do
        V.length factsFromSPDX `shouldBe` 14
      it "there is a 0BSD SPDXFact" $ do
        (nBSD `containsFactOfType` "SPDXEntry") `shouldBe` (True :: Bool)
      it "there is no ABC SPDXFact" $ do
        (abc `containsFactOfType` "SPDXEntry") `shouldBe` (False :: Bool)

  describe "Collector.BlueOak" $ let
      factsFromEmptyBlueOak = loadBlueOakFactsFromString blueOakEmptyExample
      factsFromMiniBlueOak = loadBlueOakFactsFromString blueOakMiniExample
      factsFromBlueOak = loadBlueOakFactsFromString blueOakExample

      abc = getLicenseFromFacts "ABC" [] factsFromBlueOak
      mit = getLicenseFromFacts "MIT" [] factsFromBlueOak
    in do
      it "it is possible to parse the empty json string" $ do
        show (decodeBlueOakData blueOakEmptyExample) `shouldBe` "BlueOakData {version = \"1\", ratings = []}"
      it "it is possible to parse the empty json string" $ do
        V.length factsFromEmptyBlueOak `shouldBe` 0
      it "it is possible to parse the mini json string" $ do
        V.length factsFromMiniBlueOak `shouldBe` 3
      it "it is possible to parse the string" $ do
        V.length factsFromBlueOak `shouldBe` 169

      it "there is a MIT BlueOakEntryFact" $ do
        (mit `containsFactOfType` "BOEntry") `shouldBe` (True :: Bool)

  describe "Collector.OpenChainPolicyTemplate" $ let
      factsFromOCPT = loadOCPTFactsFromString ocptExample
      mit = getLicenseFromFacts "MIT" [] factsFromOCPT
    in do
      it "it is possible to parse the csv" $ do
        V.length factsFromOCPT `shouldBe` 5
      it "it contains a MIT line" $ do
        (mit `containsFactOfType` "OCPTRow") `shouldBe` (True :: Bool)

  describe "Collectors.ChooseALicense" $ let
      ls = lines (Char8.unpack chooseALicenseExample)
    in do
      it "it finds the condition" $ do
        extractListFromText ls "conditions" `shouldBe` ["include-copyright"]

  describe "Collectors.Gnu" $ let
      parsedEmpty = loadGnuFactsFromByteString True False gnuEmptyDocument
      parsedSingle = loadGnuFactsFromByteString True False gnuSingleDocument
      parsedDouble = loadGnuFactsFromByteString True False gnuDoubleDocument
      factsFromEmpty = fromRight undefined parsedEmpty
      factsFromSingle = fromRight undefined parsedSingle
      factsFromDouble = fromRight undefined parsedDouble
    in do
      it "can parse empty" $ do
        parsedEmpty `shouldSatisfy` isRight
        V.length factsFromEmpty `shouldBe` 0
      it "can parse single" $ do
        parsedSingle `shouldSatisfy` isRight
        V.length factsFromSingle `shouldBe` 1
      it "can parse double" $ do
        parsedDouble `shouldSatisfy` isRight
        V.length factsFromDouble `shouldBe` 2

  describe "Lib" $ do
    it "it finds some facts" $ do
      fs <- readFacts "./data"
      fs `shouldSatisfy` (\fs' -> (V.length fs') >= 2698)
