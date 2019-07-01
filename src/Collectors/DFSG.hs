{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes #-}
{-
 - https://wiki.debian.org/DFSGLicenses
 -}
module Collectors.DFSG
  ( loadDFSGFacts
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

data DFSGEntry
  = DFSGEntry
  { dfsgLicName :: LicenseName
  , dfsgState   :: DFSGState
  }

instance LFRaw DFSGEntry where
  getLicenseFactClassifier _ = LFC ["DebianFreeSoftwareGuidelines"]
  getImpliedNames de = [dfsgLicName de]

dfsgEntries
  -- DFSG-compatible Licenses
  = map (\n -> DFSGEntry n DFSGInCompatible)
        [ "GNU AFFERO GENERAL PUBLIC LICENSE (AGPL-3)"
        , "Artistic License"
        , "The Apache Software License (ASL)"
        , "The BSD-3-clause License"
        , "Creative Commons Attribution Share-Alike (CC-BY-SA) v4.0"
        , "Creative Commons Attribution Share-Alike (CC-BY-SA) v3.0"
        , "Creative Commons Attribution unported (CC-BY) v3.0"
        , "Creative Commons Attribution unported (CC-BY) v4.0"
        , "Common Public License (CPL), Version 1.0"
        , "IBM Public License, Version 1.0"
        , "Eclipse Public License - 1.0"
        , "The GNU General Public License (GPL)"
        , "The GNU Lesser General Public License (LGPL)"
        , "The MIT License"
        , "The SIL Open Font License"
        , "Mozilla Public License (MPL)"
        , "DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE"
        , "The zlib/libpng License (Zlib)"
        ]
  -- Other DFSG compatible licenses
  ++ map (\n -> DFSGEntry n DFSGInCompatible)
         [ "ISC license"
         , "The MirOS Licence"
         ]
  -- Licenses whose status is unsettled
  ++ map (\n -> DFSGEntry n DFSGStateUnsettled)
         [ "Q Public License (QPL), Version 1.0"
         , "X-Oz License"
         , "Licence Art Libre (Free Art License)"
         ]
  -- Licenses that are DFSG-incompatible
  ++ map (\n -> DFSGEntry n DFSGInCompatible)
         [ "Apple Public Source License (APSL)"
         , "GNU Free Documentation License (GFDL)"
         , "Open Publication License (OPL) v1.0"
         , "Open Software License (OSL) v1.1"
         , "Creative Commons Attribution License (CC-by), v1.0"
         , "Creative Commons Attribution-Non Commercial-Share Alike (CC-by-nc-sa)"
         , "Creative Commons Attribution-Share Alike Generic (CC-BY-SA), v1.0"
         , "Creative Commons Sampling Plus (CC-sampling+), v1.0"
         , "JSON evil license"
         , "License for OpenPBS and Torque"
         , "Swiss Ephemeris Public License"
         , "RealNetworks Public Source License (RPSL)"
         , "SPIN License"
         , "Common Public Attribution License"
         ]

loadWikipediaFacts :: IO Facts
loadWikipediaFacts = do
  logThatFactsAreLoadedFrom "DebianFreeSoftwareGuidelines (DFSG)"
  return . V.fromList $ map LicenseFact dfsgEntries
