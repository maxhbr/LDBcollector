{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-
 - this contains informations from the google oss policy:
 - - https://opensource.google.com/docs/thirdparty/licenses/
 -}
module Collectors.Google
    ( loadGoogleFacts
    ) where

import qualified Prelude as P
import           MyPrelude
import           Collectors.Common

import qualified Data.Vector as V

import           Model.License

data GoogleClassification
  = RESTRICTED
  | RESTRICTED_IF_STATICALLY_LINKED
  | RECIPROCAL
  | NOTICE
  | PERMISSIVE
  | BY_EXCEPTION_ONLY
  | UNENCUMBERED
  | CANNOT_BE_USED Text
  deriving (Eq, Show, Generic)
instance ToJSON GoogleClassification where
  toJSON RESTRICTED                      = "RESTRICTED"
  toJSON RESTRICTED_IF_STATICALLY_LINKED = "RESTRICTED_IF_STATICALLY_LINKED"
  toJSON RECIPROCAL                      = "RECIPROCAL"
  toJSON NOTICE                          = "NOTICE"
  toJSON PERMISSIVE                      = "PERMISSIVE"
  toJSON BY_EXCEPTION_ONLY               = "BY_EXCEPTION_ONLY"
  toJSON UNENCUMBERED                    = "UNENCUMBERED"
  toJSON (CANNOT_BE_USED _)              = "CANNOT_BE_USED"

data GooglePolicyFact
  = GooglePolicyFact LicenseName GoogleClassification
  deriving (Show, Generic)
instance ToJSON GooglePolicyFact where
  toJSON (GooglePolicyFact licenseName r@(CANNOT_BE_USED description)) = object [ "id" .= licenseName, "rating" .= toJSON r, "description" .= description ]
  toJSON (GooglePolicyFact licenseName r)                              = object [ "id" .= licenseName, "rating" .= toJSON r ]
instance LFRaw GooglePolicyFact where
  getLicenseFactClassifier _                         = LFC ["Google", "GoogleOSSPolicy"]
  getImpliedNames (GooglePolicyFact spdxId _)        = [spdxId]
  getImpliedStatements gpf@(GooglePolicyFact _ clss) = let
      ratingFromClassification = case clss of
        RESTRICTED -> NegativeJudgement (tShow clss)
        RESTRICTED_IF_STATICALLY_LINKED -> NegativeJudgement (tShow clss)
        (CANNOT_BE_USED _) -> NegativeJudgement (tShow clss)
        BY_EXCEPTION_ONLY -> NegativeJudgement (tShow clss)
        NOTICE -> PositiveJudgement (tShow clss)
        UNENCUMBERED -> PositiveJudgement (tShow clss)
        PERMISSIVE -> PositiveJudgement (tShow clss)
        _ -> NeutralJudgement (tShow clss)
    in SLSR (getLicenseFactClassifier gpf)

restrictedLicenses :: Vector GooglePolicyFact
restrictedLicenses = let
    rows =
      -- BCL
      [ "BCL"
      -- Creative Commons “Attribution-ShareAlike” (CC BY-SA) and “Attribution-NoDerivs” (CC BY-ND) licenses
      , "CC-BY-ND-1.0", "CC-BY-ND-2.0", "CC-BY-ND-2.5", "CC-BY-ND-3.0", "CC-BY-ND-4.0"
      , "CC-BY-SA-1.0", "CC-BY-SA-2.0", "CC-BY-SA-2.5", "CC-BY-SA-3.0", "CC-BY-SA-4.0"
      -- GNU Classpath’s GPL + exception
      -- GNU GPL v1, v2, v3
      , "GPL-1.0-only", "GPL-1.0-or-later", "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later"
      -- GNU LGPL v2.1, v3 (though marked as restricted, LGPL-licensed components can be used without observing all of the restricted-type requirements if the component is dynamically-linked).
      , "LGPL-2.0-only", "LGPL-2.0-or-later", "LGPL-2.1-only", "LGPL-2.1-or-later", "LGPL-3.0-only", "LGPL-3.0-or-later"
      -- Netscape Public License NPL 1.0 and NPL 1.1
      , "NPL-1.0", "NPL-1.1"
      -- OSL
      , "OSL-1.0", "OSL-1.1", "OSL-2.0", "OSL-2.1", "OSL-3.0"
      -- QPL
      , "QPL-1.0"
      -- Sleepycat License
      , "Sleepycat"
      -- qmail Terms of Distribution
      ]
  in V.fromList $ map (`GooglePolicyFact` RESTRICTED) rows

reciprocalLicenses :: Vector GooglePolicyFact
reciprocalLicenses = let
  rows =
    -- Common Development and Distribution License CDDL 1.0, CDDL 1.1
    [ "CDDL-1.0", "CDDL-1.1"
    -- CeCILL-C License
    , "CECILL-C"
    -- CPL 1.0
    , "CPL-1.0"
    -- EPL 1.0 and EPL 2.0 (Eclipse Public License)
    , "EPL-1.0", "EPL-2.0"
    -- IPL 1.0 (IBM Public License)
    , "IPL-1.0"
    -- Mozilla Public License MPL 1.0, MPL 1.1, and MPL 2.0
    , "MPL-1.0", "MPL-1.1", "MPL-2.0"
    -- Apple Public Source License (APSL) 2.0
    , "APSL-2.0"
    -- Ruby
    , "Ruby"
    ]
  in V.fromList $ map (`GooglePolicyFact` RECIPROCAL) rows

noticeLicenses :: Vector GooglePolicyFact
noticeLicenses = let
  rows =
    -- AFL 2.1 and AFL 3.0
    [ "AFL-2.1", "AFL-3.0"
    -- Apache License 2.0
    , "Apache-2.0"
    -- Artistic License 1.0 and Artistic License 2.0
    , "Artistic-1.0", "Artistic-2.0"
    -- ASL 1.1 (Apache Software License 1.1)
    , "Apache-1.1"
    -- Autodesk DWF Toolkit
    -- Boost Software License
    , "BSL-1.0"
    -- BSD (occasionally referred to as the “University of California” license)
    , "BSD-4-Clause", "BSD-4-Clause-UC"
    -- BSD 3-clause (sometimes called BSD-new)
    , "BSD-3-Clause"
    -- Creative Commons “Attribution” (CC BY) license
    , "CC-BY-1.0" , "CC-BY-2.0" , "CC-BY-2.5" , "CC-BY-3.0" , "CC-BY-4.0"
    -- JSON License (MIT license with the added note: “The Software shall be used for Good, not Evil.”)
    , "JSON"
    -- Eclipse Distribution License (BSD variant)
    -- FreeType Project License
    , "FTL"
    -- ISC License
    , "ISC"
    -- libjpeg-turbo
    -- LibTIFF
    , "libtiff"
    -- Lucent Public License 1.02 (used by Plan 9 now, but different from “the Plan 9 license”)
    , "LPL-1.02"
    -- Microsoft Public License (MS-PL)
    , "MS-PL"
    -- MIT/X11/Expat
    , "MIT"
    -- NCSA
    , "NCSA"
    -- OpenSSL
    , "OpenSSL"
    -- PHP License 2.02 and 3.0
    , "PHP-3.0"
    -- PostgreSQL License
    , "PostgreSQL"
    -- Python Software Foundation
    , "Python-2.0"
    -- TCP Wrappers
    , "TCP-wrappers"
    -- Unicode, Inc. License Agreement - Data Files and Software
    , "Unicode-DFS-2015", "Unicode-DFS-2016"
    -- W3C Software license
    , "W3C", "W3C-19980720", "W3C-20150513"
    -- X.Net
    , "Xnet"
    -- Zend Engine License, v2.00
    , "Zend-2.0"
    -- zlib/libpng
    , "Zlib"
    -- ZPL
    , "ZPL-1.1", "ZPL-2.0", "ZPL-2.1"
    ]
  in V.fromList $ map (`GooglePolicyFact` NOTICE) rows

unencumberedLicenses :: Vector GooglePolicyFact
unencumberedLicenses = let
    rows =
      -- Creative Commons CC0 (public domain dedication)
      [ "CC0-1.0"
      -- Unlicense
      , "Unlicense"
      ]
  in V.fromList $ map (`GooglePolicyFact` UNENCUMBERED) rows

cannotBeUsedLicenses :: Vector GooglePolicyFact
cannotBeUsedLicenses = let
  rows =
    -- AGPL (Affero GPL) not allowed
    -- Code released under the GNU Affero General Public License (AGPL) cannot be used in google3 under any circumstances, and only very rarely on workstations. Read more at go/agpl.
    [ ("AGPL-3.0", "Code released under the GNU Affero General Public License (AGPL) cannot be used in google3 under any circumstances, and only very rarely on workstations. Read more at go/agpl")
    , ("AGPL-1.0", "Code released under the GNU Affero General Public License (AGPL) cannot be used in google3 under any circumstances, and only very rarely on workstations. Read more at go/agpl")
    -- CPAL not allowed
    -- Likewise, code released under the Common Public Attribution License (CPAL), notably the Mule ESB and most of the code that backs Reddit, cannot be used at Google; it is AGPL-like in crucial ways and is disallowed for the same reasons.
    , ("CPAL-1.0", "Likewise, code released under the Common Public Attribution License (CPAL), notably the Mule ESB and most of the code that backs Reddit, cannot be used at Google; it is AGPL-like in crucial ways and is disallowed for the same reasons.")
    -- European Union Public Licence (EUPL) not allowed
    -- The EUPL is very similar to the AGPL. For the same reasons that the AGPL is banned, the use of EUPL-licensed software is not allowed at Google.
    , ("EUPL-1.0", "The EUPL is very similar to the AGPL. For the same reasons that the AGPL is banned, the use of EUPL-licensed software is not allowed at Google.")
    , ("EUPL-1.1", "The EUPL is very similar to the AGPL. For the same reasons that the AGPL is banned, the use of EUPL-licensed software is not allowed at Google.")
    , ("EUPL-1.2", "The EUPL is very similar to the AGPL. For the same reasons that the AGPL is banned, the use of EUPL-licensed software is not allowed at Google.")
    -- SISSL not allowed
    -- Code released under the Sun Industry Standards Source License (SISSL) cannot be used at Google. This license has terms that are very difficult to comply with (even Sun, before being acquired, ceased to use or recommend this license). Source files related to sFlow sometimes are released under this license, but are typically also available under a slightly less onerous sFlow License.
    , ("SISSL", "Code released under the Sun Industry Standards Source License (SISSL) cannot be used at Google. This license has terms that are very difficult to comply with (even Sun, before being acquired, ceased to use or recommend this license). Source files related to sFlow sometimes are released under this license, but are typically also available under a slightly less onerous sFlow License.")
    , ("SISSL-1.2", "Code released under the Sun Industry Standards Source License (SISSL) cannot be used at Google. This license has terms that are very difficult to comply with (even Sun, before being acquired, ceased to use or recommend this license). Source files related to sFlow sometimes are released under this license, but are typically also available under a slightly less onerous sFlow License.")
    -- Watcom-1.0 not allowed
    -- Code released under the Sybase Open Watcom Public License version 1.0 cannot be used at Google. Provision 12.1© terminates the license if any patent litigation is filed against Sybase or any contributor, including cross claims and counterclaims, without limiting the scope of this provision to patent litigation concerning the specific software being licensed. This provision goes too far in restricting the exercise of Google’s patent rights and is therefore prohibited at Google.
    , ("Watcom-1.0", "Code released under the Sybase Open Watcom Public License version 1.0 cannot be used at Google. Provision 12.1© terminates the license if any patent litigation is filed against Sybase or any contributor, including cross claims and counterclaims, without limiting the scope of this provision to patent litigation concerning the specific software being licensed. This provision goes too far in restricting the exercise of Google’s patent rights and is therefore prohibited at Google.")
    -- WTFPL not allowed
    -- Code released under the WTFPL cannot be used at Google. This license has a large number of issues (lack of warranty disclaimer, very vague rights grant), and was also rejected as an open source license by OSI. We also do not allow contribution to projects under the WTFPL.
    , ("WTFPL", "Code released under the WTFPL cannot be used at Google. This license has a large number of issues (lack of warranty disclaimer, very vague rights grant), and was also rejected as an open source license by OSI. We also do not allow contribution to projects under the WTFPL.")
    -- The Beerware license has similar issues to the WTFPL on account of its vague grant of rights and likewise cannot be used at Google, nor can Beerware-licensed projects be patched by Googlers.
    , ("Beerware", "The Beerware license has similar issues to the WTFPL on account of its vague grant of rights and likewise cannot be used at Google, nor can Beerware-licensed projects be patched by Googlers.")
    -- Commons Clause not allowed
    -- The Commons Clause prohibits any commercial use of the software. As with the above, everything that Google undertakes is a commercial endeavor, so no code released under any license that includes the Common Clause may be used at Google.
    , ("Commons Clause", "The Commons Clause prohibits any commercial use of the software. As with the above, everything that Google undertakes is a commercial endeavor, so no code released under any license that includes the Common Clause may be used at Google.")
    ]
    -- “Non-Commercial” licenses not allowed
    -- Everything that Google undertakes, including research, is considered a commercial endeavor, so no code released under a license that restricts it to non-commercial uses may be used at Google. For example, works under any Creative Commons licenses containing NC (CC BY-NC, CC BY-NC-SA, CC BY-NC-ND) may not be used at Google.
    ++ (map (\spdxId -> (spdxId, "Everything that Google undertakes, including research, is considered a commercial endeavor, so no code released under a license that restricts it to non-commercial uses may be used at Google. For example, works under any Creative Commons licenses containing NC (CC BY-NC, CC BY-NC-SA, CC BY-NC-ND) may not be used at Google."))
            [ "CC-BY-NC-1.0", "CC-BY-NC-2.0", "CC-BY-NC-2.5", "CC-BY-NC-3.0", "CC-BY-NC-4.0"
            , "CC-BY-NC-ND-1.0", "CC-BY-NC-ND-2.0", "CC-BY-NC-ND-2.5", "CC-BY-NC-ND-3.0", "CC-BY-NC-ND-4.0"
            , "CC-BY-NC-SA-1.0", "CC-BY-NC-SA-2.0", "CC-BY-NC-SA-2.5", "CC-BY-NC-SA-3.0", "CC-BY-NC-SA-4.0" ])
  in V.fromList $ map (\(spdxId, description) -> GooglePolicyFact spdxId (CANNOT_BE_USED description)) rows

loadGoogleFacts :: IO Facts
loadGoogleFacts = do
  logThatFactsAreLoadedFrom "Google OSS Policy"
  return $ V.map (LicenseFact "https://opensource.google.com/docs/thirdparty/licenses/") (V.concat [ restrictedLicenses
                                                                                                   , reciprocalLicenses
                                                                                                   , noticeLicenses
                                                                                                   , unencumberedLicenses
                                                                                                   , cannotBeUsedLicenses])

