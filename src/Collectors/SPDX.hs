{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Collectors.SPDX
  ( loadSPDXFacts
  , loadSPDXFactsFromString
  ) where

import           System.FilePath
import           System.IO
import qualified Data.Text as T
import qualified Data.Vector as V
import           Debug.Trace (trace)
import qualified Data.ByteString.Char8 as C8
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)

import           Data.Aeson
import           GHC.Generics

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
  getImpliedShortnames e        = [spdxLicenseId e]
  getType _                     = "SPDXEntry"

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
  Just (SPDXList v es _)  -> trace ("SPDX License list version is: " ++ v) $ let
      filteredEs = filter (\f -> not $ isSPDXLicenseDeprecated f) es
    in V.fromList $ map (mkLicenseFact "SPDX") filteredEs
  Nothing                 -> V.empty


-- example filepath: ../data/spdx-license-list-data/json
loadSPDXFacts :: FilePath -> IO Facts
loadSPDXFacts basepath = let
    licensesJSONFile = basepath </> "licenses.json"
  in do
    hPutStrLn stderr $ "DEBUG: parse SPDX file: " ++ licensesJSONFile
    bs <- B.readFile licensesJSONFile
    return (loadSPDXFactsFromString bs)
