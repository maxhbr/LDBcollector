{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.Fossology
  ( fossologyLFC
  , loadFossologyFacts
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id)

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.ByteString
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import           Data.FileEmbed (embedFile)

import           Debug.Trace (trace)

import           Model.License
import           Collectors.Common

fossologyLFC :: LicenseFactClassifier
fossologyLFC = LFCWithURLAndLicense "https://github.com/fossology/fossology/blob/master/install/db/licenseRef.json" (LFLWithURL "https://github.com/fossology/fossology/blob/master/LICENSE" "GPL-2.0-only") "Fossology licenseRef"

data FossologyFact
  = FossologyFact
  { rf_shortname :: LicenseName
  , rf_text :: Text
  , rf_url :: URL
-- , rf_add_date ::
-- , rf_copyleft :: -- always null?
-- , rf_OSIapproved :: -- always null?
, rf_fullname :: LicenseName
-- , rf_FSFfree ::  -- always null?
-- , rf_GPLv2compatible :: -- always null?
-- , rf_GPLv3compatible :: -- always null?
, rf_notes :: Maybe String
-- , rf_Fedora ::  -- always null?
-- , marydone ::
-- , rf_active ::
-- , rf_text_updatable ::
-- , rf_detector_type ::
-- , rf_source :: -- always null?
-- , rf_risk :: -- always null?
-- , rf_spdx_compatible ::
-- , rf_flag ::
 } deriving (Show,Generic)
instance FromJSON FossologyFact
instance ToJSON FossologyFact
instance LicenseFactClassifiable FossologyFact where
  getLicenseFactClassifier _ = fossologyLFC
instance LFRaw FossologyFact where
  getImpliedFullName f = mkRLSR f 35 (rf_fullname f)
  getImpliedNames f    = CLSR [rf_shortname f, rf_fullname f]
  getImpliedURLs f     = CLSR [(Nothing, rf_url f)]
  getImpliedComments f = case rf_notes f of
    Just n  -> mkSLSR f [n]
    Nothing -> NoSLSR

decodeFossologyData :: ByteString -> [FossologyFact]
decodeFossologyData bs = case eitherDecode bs of
  Right fossologyData -> fossologyData
  Left err            -> trace err undefined -- TODO

loadFossologyFactsFromString :: ByteString -> Facts
loadFossologyFactsFromString bs = let
    fossologyData = decodeFossologyData bs
  in V.fromList (map (LicenseFact Nothing) fossologyData)

loadFossologyFacts :: IO Facts
loadFossologyFacts = let
    fossologyFile :: Data.ByteString.ByteString
    fossologyFile = $(embedFile "data/fossology/licenseRef.json")
  in do
    logThatFactsAreLoadedFrom "Fossology licenseRef"
    return (loadFossologyFactsFromString (B.fromStrict fossologyFile))
