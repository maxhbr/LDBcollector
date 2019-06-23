{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE TupleSections #-}
module Collectors.SPDX
  ( loadSPDXFacts
  , loadSPDXFactsFromString
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id, ByteString)
import           Collectors.Common

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString.Char8 as C8
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)

import           Model.License

{-
  Example JSON snippet:
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
    }
-}

data SPDXEntry
  = SPDXEntry
  { spdxLicenseId :: String
  , spdxFullName :: String
  , isSPDXLicenseDeprecated :: Bool
  , spdxDetailsURL :: String
  , spdxSeeAlso :: [String]
  , spdxLicIsOSIApproved :: Bool
  } deriving (Show, Generic)
instance ToJSON SPDXEntry
instance FromJSON SPDXEntry where
  parseJSON = withObject "SPDXEntry" $ \v -> SPDXEntry
    <$> v .: "licenseId"
    <*> v .: "name"
    <*> v .: "isDeprecatedLicenseId"
    <*> v .: "detailsUrl"
    <*> v .: "seeAlso"
    <*> v .: "isOsiApproved"
instance LFRaw SPDXEntry where
  getLicenseFactClassifier _ = LFC ["SPDX", "SPDXEntry"]
  getImpliedNames e          = CLSR [spdxLicenseId e, spdxFullName e]
  getImpliedId e             = RLSR 100 (spdxLicenseId e)
  getImpliedURLs e           = CLSR $ [("SPDX details", spdxDetailsURL e)] ++ (map ("see also",) (spdxSeeAlso e))

data SPDXList
  = SPDXList String [SPDXEntry] String
  deriving (Show)
instance FromJSON SPDXList where
  parseJSON = withObject "SPDXList" $ \v -> SPDXList
    <$> v .: "licenseListVersion"
    <*> v .: "licenses"
    <*> v .: "releaseDate"

loadSPDXFactsFromString :: ByteString -> Facts
loadSPDXFactsFromString s = case (decode s :: Maybe SPDXList) of
  Just (SPDXList v es _)  -> trace ("INFO: SPDX License list version is: " ++ v) $ let
      filteredEs = filter (not . isSPDXLicenseDeprecated) es
    in V.fromList $ map (\f -> LicenseFact (Just $ "https://spdx.org/licenses/" ++ spdxLicenseId f ++ ".html") f) filteredEs
  Nothing                 -> V.empty


-- example filepath: ../data/spdx-license-list-data/json
loadSPDXFacts :: FilePath -> IO Facts
loadSPDXFacts basepath = let
    licensesJSONFile = basepath </> "licenses.json"
  in do
    logThatFactsAreLoadedFrom "SPDX License List"
    hPutStrLn stderr $ "INFO: parse SPDX file: " ++ licensesJSONFile
    bs <- B.readFile licensesJSONFile
    return (loadSPDXFactsFromString bs)
