{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.LicenseCompatibility
  ( licenseCompatibilityLFC
  , loadLicenseCompatibilityFacts
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

licenseCompatibilityLFC :: LicenseFactClassifier
licenseCompatibilityLFC = let
  url = "https://github.com/librariesio/license-compatibility/blob/master/lib/license/licenses.json"
  lic = (LFLWithURL "https://github.com/librariesio/license-compatibility/blob/master/LICENSE.txt" "MIT")
  in LFCWithURLAndLicense url lic "librariesio license-compatibility"

{-
-- https://github.com/librariesio/license-compatibility

    {
      "public_domain": [
        "CC0-1.0",
        ...
      ],
      "permissive": [
        "AFL-1.1",
        ...
      ],
      "weak_copyleft": [
        "EPL-1.0",
        ...
      ],
      "strong_copyleft": [
        "GPL-3.0",
        ...
      ],
      "network_copyleft": [
        "AGPL-1.0",
        ...
      ]
    }
-}

data LicenseCompatibilityJSON
  = LicenseCompatibilityJSON
  { public_domain :: [LicenseName]
  , permissive :: [LicenseName]
  , weak_copyleft :: [LicenseName]
  , strong_copyleft :: [LicenseName]
  , network_copyleft :: [LicenseName]
  } deriving (Show,Generic)
instance FromJSON LicenseCompatibilityJSON


data LicenseCompatibilityFact
  = LicenseCompatibilityFact
  { licensename :: LicenseName
  , copyleftkind :: CopyleftKind
  } deriving (Eq, Show, Generic)
instance ToJSON LicenseCompatibilityFact
instance LicenseFactClassifiable LicenseCompatibilityFact where
  getLicenseFactClassifier _ = licenseCompatibilityLFC
instance LFRaw LicenseCompatibilityFact where
  getImpliedNames (LicenseCompatibilityFact ln _)       = CLSR [ln]
  getImpliedCopyleft boe@(LicenseCompatibilityFact _ c) = mkSLSR boe c

factsFromJSON :: LicenseCompatibilityJSON -> Facts
factsFromJSON (LicenseCompatibilityJSON pd p wc sc nc) = (V.fromList . map (LicenseFact Nothing) . concat)
  [ map (`LicenseCompatibilityFact` NoCopyleft) (pd ++ p)
  , map (`LicenseCompatibilityFact` WeakCopyleft) wc
  , map (`LicenseCompatibilityFact` StrongCopyleft) sc
  , map (`LicenseCompatibilityFact` SaaSCopyleft) nc
  ]

loadLicenseCompatibilityFactsFromString :: ByteString -> Facts
loadLicenseCompatibilityFactsFromString bs = case eitherDecode bs of
  Right lcj -> factsFromJSON lcj
  Left err  -> trace ("ERR: Failed to parse JSON: " ++ err) undefined

loadLicenseCompatibilityFacts :: IO Facts
loadLicenseCompatibilityFacts = let
    loadLicenseCompatibilityFile :: Data.ByteString.ByteString
    loadLicenseCompatibilityFile = $(embedFile "data/librariesio-license-compatibility/licenses.json")
  in do
    logThatFactsAreLoadedFrom "librariesio license-compatibility"
    return (loadLicenseCompatibilityFactsFromString (B.fromStrict loadLicenseCompatibilityFile))
