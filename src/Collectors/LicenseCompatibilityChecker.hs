{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.LicenseCompatibilityChecker
  ( licenseCompatibilityCheckerLFC
  , loadLicenseCompatibilityCheckerFacts
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

licenseCompatibilityCheckerLFC :: LicenseFactClassifier
licenseCompatibilityCheckerLFC = let
  url = "https://github.com/HansHammel/license-compatibility-checker/blob/master/lib/licenses.json"
  lic = LFLWithURL "https://github.com/HansHammel/license-compatibility-checker/blob/master/LICENSE" "MIT"
  in LFCWithURLAndLicense url lic "HansHammel license-compatibility-checker"

{-
-- https://github.com/HansHammel/license-compatibility-checker
{
    "Public Domain": [
        "CC0-1.0",
        ...
    ],
    "Permissive": [
        "AFL-1.1",
        ....
    ],
    "Weakly Protective": [
        "LGPL-2.0",
         ...
    ],
    "Strongly Protective": [
        "CPL-1.0",
        ...
    ],
    "Network Protective": [
        "AGPL-1.0",
        "AGPL-3.0"
    ],
    "Uncategorized": [
        "0BSD",
        ...
    ]
}
-}

data LicenseCompatibilityCheckerJSON
  = LicenseCompatibilityCheckerJSON
  { public_domain :: [LicenseName]
  , permissive :: [LicenseName]
  , weak_copyleft :: [LicenseName]
  , strong_copyleft :: [LicenseName]
  , network_copyleft :: [LicenseName]
  } deriving (Show,Generic)
instance FromJSON LicenseCompatibilityCheckerJSON where
  parseJSON = withObject "LicenseCompatibilityCheckerJSON" $ \v -> LicenseCompatibilityCheckerJSON
    <$> v .: "Public Domain"
    <*> v .: "Permissive"
    <*> v .: "Weakly Protective"
    <*> v .: "Strongly Protective"
    <*> v .: "Network Protective"

data LicenseCompatibilityCheckerFact
  = LicenseCompatibilityCheckerFact
  { licensename :: LicenseName
  , copyleftkind :: CopyleftKind
  } deriving (Eq, Show, Generic)
instance ToJSON LicenseCompatibilityCheckerFact
instance LicenseFactClassifiable LicenseCompatibilityCheckerFact where
  getLicenseFactClassifier _ = licenseCompatibilityCheckerLFC
instance LFRaw LicenseCompatibilityCheckerFact where
  getImpliedNames (LicenseCompatibilityCheckerFact ln _)       = CLSR [ln]
  getImpliedCopyleft boe@(LicenseCompatibilityCheckerFact _ c) = mkSLSR boe c

factsFromJSON :: LicenseCompatibilityCheckerJSON -> Facts
factsFromJSON (LicenseCompatibilityCheckerJSON pd p wc sc nc) = (V.fromList . map (LicenseFact Nothing) . concat)
  [ map (`LicenseCompatibilityCheckerFact` NoCopyleft) (pd ++ p)
  , map (`LicenseCompatibilityCheckerFact` WeakCopyleft) wc
  , map (`LicenseCompatibilityCheckerFact` StrongCopyleft) sc
  , map (`LicenseCompatibilityCheckerFact` SaaSCopyleft) nc
  ]

loadLicenseCompatibilityCheckerFactsFromString :: ByteString -> Facts
loadLicenseCompatibilityCheckerFactsFromString bs = case eitherDecode bs of
  Right lcj -> factsFromJSON lcj
  Left err  -> trace ("ERR: Failed to parse JSON: " ++ err) undefined

loadLicenseCompatibilityCheckerFacts :: IO Facts
loadLicenseCompatibilityCheckerFacts = let
    loadLicenseCompatibilityCheckerFile :: Data.ByteString.ByteString
    loadLicenseCompatibilityCheckerFile = $(embedFile "data/HansHammel-license-compatibility-checker/licenses.json")
  in do
    logThatFactsAreLoadedFrom "HansHammel license-compatibility-checker"
    return (loadLicenseCompatibilityCheckerFactsFromString (B.fromStrict loadLicenseCompatibilityCheckerFile))
