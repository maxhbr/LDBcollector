{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes #-}
{-
 - https://wiki.debian.org/DFSGLicenses
 -}
module Collectors.DFSG
  ( loadDFSGFacts
  , dfsgLFC
  ) where

import qualified Prelude as P
import           MyPrelude
import           Collectors.Common

import qualified Data.Vector as V

import           Model.License

data DFSGState
  = DFSGCompatible
  | DFSGStateUnsettled
  | DFSGInCompatible
  deriving (Show, Generic)

instance ToJSON DFSGState

data DFSGEntry
  = DFSGEntry
  { dfsgLicName :: LicenseName
  , dfsgLicId   :: Maybe LicenseName
  , dfsgState   :: DFSGState
  , dfsgComment :: Maybe String
  } deriving (Show, Generic)

instance ToJSON DFSGEntry where
  toJSON (DFSGEntry n i s c) = object [ "LicenseName" .= n
                                      , "LicenseId" .= i
                                      , "State" .= s
                                      , "Comment" .= c
                                      ]

dfsgLFC :: LicenseFactClassifier
dfsgLFC = LFCWithLicense (LFL "NOASSERTION") "Debian Free Software Guidelines"
instance LicenseFactClassifiable DFSGEntry where
  getLicenseFactClassifier _ = dfsgLFC
instance LFRaw DFSGEntry where
  getImpliedNames de         = case dfsgLicId de of
    Just i  -> CLSR [i]
    Nothing -> CLSR [dfsgLicName de]
  getImpliedAmbiguousNames de = CLSR [dfsgLicName de]
  getImpliedJudgement e@(DFSGEntry _ _ s c) = let
      defaultMessage = case s of
                         DFSGCompatible -> "This license is compatible with the DebianFreeSoftwareGuidelines (DFSG-free)"
                         DFSGStateUnsettled -> "It is currently unstettled whether this license is DFSG-free"
                         DFSGInCompatible -> "This license is not compatible with the DebianFreeSoftwareGuidelines (DFSG-unfree)"
      defaultJudgement m = mkSLSR e $ case s of
                                        DFSGCompatible -> PositiveJudgement m
                                        DFSGStateUnsettled -> NeutralJudgement m
                                        DFSGInCompatible -> NegativeJudgement m
    in case c of
      Just m  -> defaultJudgement m
      Nothing -> defaultJudgement defaultMessage

dfsgEntries :: [DFSGEntry]
dfsgEntries = let
    tupleToEntry state (name, [], "") = [ DFSGEntry name Nothing state Nothing ]
    tupleToEntry state (name, [], c) = [ DFSGEntry name Nothing state (Just c) ]
    tupleToEntry state (name, ids, "") = map (\i -> DFSGEntry name (Just i) state Nothing) ids
    tupleToEntry state (name, ids, c) = map (\i -> DFSGEntry name (Just i) state (Just c)) ids
  -- DFSG-compatible Licenses
  in concatMap (tupleToEntry DFSGCompatible)
        [ ("GNU AFFERO GENERAL PUBLIC LICENSE (AGPL-3)", ["AGPL-3.0-only", "GPL-3.0-or-later"], "")
        , ("Artistic License", ["Artistic-1.0", "Artistic-1.0-cl8", "Artistic-1.0-Perl"], "Do note that the Artistic License is considered non-free by the FSF. They suggest to use the Clarified Artistic License (also called Artistic License 2.0) instead. However, the original Artistic License is still considered DFSG-free.")
        , ("Artistic License", ["Artistic-2.0"], "")
        , ("The Apache Software License (ASL)", ["Apache-2.0", "Apache-1.1", "Apache-1.0"], "Older versions of the Apache License (1.0 and 1.1) are also DFSG free, but the Apache Software Foundation recommends using the Apache 2.0 license instead.")
        , ("The BSD-3-clause License", ["BSD-3-Clause", "BSD-3-Clause-Clear"], "Note that a 2-clause form of the BSD license, removing the third condition, is also in use. This is because even a generous copyright license does not implicitly forfeit the copyright holder's \"right of publicity\". In other words, even if a license does not forbid you from claiming that the copyright holder or other parties endorses or promotes your work, the law generally does. We're not aware of any exceptions.")
        , ("Creative Commons Attribution Share-Alike (CC-BY-SA) v4.0", ["CC-BY-SA-4.0"], "Version 4.0 is considered to be compatible to the DFSG. Changes from the previous version are discussed in a thread starting at https://lists.debian.org/3172728.oiOx47Q9HF@debstor")
        , ("Creative Commons Attribution Share-Alike (CC-BY-SA) v3.0", ["CC-BY-SA-3.0"], "In contrast to the CC-SA 1.0 license, version 3.0 is considered to be compatible to the DFSG. In addition, the version 2.0 and 2.5 are NOT transitively compatible because of clause 4b, since that only allows redistribution of derivative works under later versions of the license.")
        , ("Creative Commons Attribution unported (CC-BY) v3.0", ["CC-BY-3.0"], "")
        , ("Creative Commons Attribution unported (CC-BY) v4.0", ["CC-BY-4.0"], "")
        , ("Common Public License (CPL), Version 1.0", ["CPL-1.0"], "")
        , ("IBM Public License, Version 1.0", ["IPL-1.0"], "This license was later renamed the Common Public License (CPL). It is used for OpenAFS and Postfix and has been accepted in Debian main since 2000.")
        , ("Eclipse Public License - 1.0", ["EPL-1.0"], "")
        , ("The GNU General Public License (GPL)", ["GPL-1.0-only", "GPL-1.0-or-later", "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later"], "This is the most popular free software license. Most of Linux (the kernel) is distributed under the GPL, as is most of the other basic software in the GNU operating system.")
        , ("The GNU Lesser General Public License (LGPL)", ["LGPL-2.0-only", "LGPL-2.0-or-later", "LGPL-2.1-only", "LGPL-2.1-or-later", "LGPL-3.0-only", "LGPL-3.0-or-later"], "Earlier called the \"Library General Public License\"; this name is deprecated because it confuses the license's intent.")
        , ("The MIT License", ["MIT"], "Exception : The University of Washington's interpretation of the MIT License, as the University interprets it for the pine email client, does not follow the DFSG. See the DebianFreeSoftwareGuidelinesDraftFAQ.")
        , ("The SIL Open Font License", ["OFL-1.0", "OFL-1.1"], "The following restriction on distributions, which is part of OFL, has been widely accepted by open source projects when it is applied to fonts: 1) Neither the Font Software nor any of its individual components, in Original or Modified Versions, may be sold by itself.")
        , ("Mozilla Public License (MPL)", ["MPL-1.0", "MPL-1.1", "MPL-2.0", "MPL-2.0-no-copyleft-exception"], "")
        , ("DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE", ["WTFPL"], "")
        , ("The zlib/libpng License (Zlib)", ["Zlib", "zlib-acknowledgement"], "")
        ]
  -- Other DFSG compatible licenses
  ++ concatMap (tupleToEntry DFSGCompatible)
         [ ("ISC license", ["ISC"], "")
         , ("The MirOS Licence", ["MirOS"], "Permissive licence, Ⓕ Copyfree, very similar to MIT and ISC but applicable to more than just software")
         ]
  -- Licenses whose status is unsettled
  ++ concatMap (tupleToEntry DFSGStateUnsettled)
         [ ("Q Public License (QPL), Version 1.0", ["QPL-1.0"], "The QPL is not GPL-compatible, which, regardless of one's opinion about the license's DFSG-freeness, poses a major practical problem for any code licensed under the QPL that is reused elsewhere in conjunction with code under the GNU GPL. This makes the QPL alone a particularly poor choice of license for a library. Furthermore, it is not clear that the Trolltech corporation (the author of the Qt library and the QPL itself) believes the QPL to be a free software license. Trolltech's website describes how their dual-license approach is intended to be \"open source-friendly\" (see http://www.trolltech.com/company/model.html). If Trolltech felt that the QPL alone were friendly enough to open-source, why do they have a dual-licensing policy?")
         , ("X-Oz License", [], "")
         , ("Licence Art Libre (Free Art License)", ["LAL-1.2", "LAL-1.3"], "")
         ]
  -- Licenses that are DFSG-incompatible
  ++ concatMap (tupleToEntry DFSGInCompatible)
         [ ("Apple Public Source License (APSL)", ["APSL-1.0", "APSL-1.1", "APSL-1.2", "APSL-2.0"], "")
         , ("GNU Free Documentation License (GFDL)", ["GFDL-1.1-only", "GFDL-1.1-or-later", "GFDL-1.2-only", "GFDL-1.2-or-later", "GFDL-1.3-only", "GFDL-1.3-or-later"], "Exception: Data licensed under the FDL with no invariant sections are considered DFSG-free as of GR 2006-001: http://www.debian.org/vote/2006/vote_001#outcome")
         , ("Open Publication License (OPL) v1.0", ["OPL-1.0"], "")
         , ("Open Software License (OSL) v1.1", ["OSL-1.1"], "")
         , ("Creative Commons Attribution License (CC-by), v1.0", ["CC-BY-1.0"], "It is believed that 2.0 still has problems (http://evan.prodromou.name/ccsummary/ccsummary.html), but it is under discussion between debian-legal and cc-licenses.")
         , ("Creative Commons Attribution-Non Commercial-Share Alike (CC-by-nc-sa)", [ "CC-BY-NC-1.0", "CC-BY-NC-2.0", "CC-BY-NC-2.5", "CC-BY-NC-3.0", "CC-BY-NC-4.0"
                                                                                     , "CC-BY-NC-ND-1.0", "CC-BY-NC-ND-2.0", "CC-BY-NC-ND-2.5", "CC-BY-NC-ND-3.0", "CC-BY-NC-ND-4.0"
                                                                                     , "CC-BY-NC-SA-1.0", "CC-BY-NC-SA-2.0", "CC-BY-NC-SA-2.5", "CC-BY-NC-SA-3.0", "CC-BY-NC-SA-4.0" ], "")
         , ("Creative Commons Attribution-Share Alike Generic (CC-BY-SA), v1.0", ["CC-BY-SA-1.0"], "")
         , ("Creative Commons Sampling Plus (CC-sampling+), v1.0", [], "")
         , ("JSON evil license", ["JSON"], "Infamous for the clause The Software shall be used for Good, not Evil.")
         , ("License for OpenPBS and Torque", [], "")
         , ("Swiss Ephemeris Public License", [], "")
         , ("RealNetworks Public Source License (RPSL)", ["RPSL-1.0"], "")
         , ("SPIN License", [], "Note that SPIN licensed software can not be distributed in non-free section")
         , ("Common Public Attribution License", ["CPAL-1.0"], "Issue: Badgeware license (see: https://lwn.net/Articles/243841/)")
         ]

loadDFSGFacts :: IO Facts
loadDFSGFacts = do
  logThatFactsAreLoadedFrom "DebianFreeSoftwareGuidelines (DFSG)"
  return . V.fromList $ map (LicenseFact (Just "https://wiki.debian.org/DFSGLicenses")) dfsgEntries
