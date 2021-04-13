{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE DeriveGeneric #-}
module Generators.FlictWriter
    ( writeFlictLicenseTranslationJSON
    ) where


import qualified Prelude as P
import           MyPrelude

import qualified Data.ByteString.Lazy as BL
import           Data.Aeson.Encode.Pretty (encodePretty)
import qualified Data.Vector as V

import           Model.License
import           Processors.ToPage (Page (..), LicenseDetails (..), unpackWithSource)


-- {
--     "meta": {
--         "software":"FOSS License Compliance Tool",
--         "type": "later-definitions",
--         "version":"0.1",
--         "description": "This file contains translation between misspelled or oddly named licenses and either SPDX or Scancode key values (used if OSADL's matrix does not support the license)"
--     },
--     "translations": [
--         {
--             "value": "&",
--             "translation": "and"
--         },
--         {
--             "value": "AMD",
--             "translation": "",
--             "comment": "who uses this???"
--         },
--         {
--             "value": "apache-1.0",
--             "translation": "Apache-1.0"
--         },
-- ...
--         {
--             "value": "GPL-2.0-with-OpenSSL-exception",
--             "translation": "",
--             "key": "",
--             "comment": "do they mean? openvpn-openssl-exception"
--         },
--         {
--             "value": "GPL-2.0-with-OpenSSL-exception",
--             "translation": null,
--             "key": "gpl-2.0-openssl",
--             "comment": "scancode key, classified as Copyleft Limited"
--         },
-- ...



-- data Meta
--   = Meta
--   { software :: String
--   , type :: String
--   , version :: String
--   , description :: String
--   } deriving (Eq, Show, Generic)
-- instance ToJSON Meta where
--     toEncoding = genericToEncoding defaultOptions
data Translation
  = Translation
  { value :: LicenseName 
  , translation :: LicenseName
  , key :: Maybe String
  , comment :: Maybe String
  } deriving (Eq, Show, Generic)
instance ToJSON Translation where
    toEncoding = genericToEncoding defaultOptions
data FlictLicenseTranslation
  = FlictLicenseTranslation
  { translations :: [Translation]
  -- ,  meta :: Meta
  } deriving (Eq, Show, Generic)
instance ToJSON FlictLicenseTranslation where
    toEncoding = genericToEncoding defaultOptions

factToTranslations :: LicenseName -> LicenseFact -> [Translation]
factToTranslations ln f = let
  names = getImpliedNonambiguousNames f
  otherNames = filter (/= ln) names
  in map (\on -> Translation ln on Nothing Nothing) otherNames

factsToTranslations :: LicenseName -> Facts -> [Translation]
factsToTranslations ln fs = concat . V.toList $ V.map (factToTranslations ln) fs

licenseToTranslations :: LicenseName -> License -> [Translation]
licenseToTranslations ln (License fs) = factsToTranslations ln fs

licensesToTranslations :: [(LicenseName, License)] -> [Translation]
licensesToTranslations [] = []
licensesToTranslations ((ln,l):ls) = licenseToTranslations ln l ++ (licensesToTranslations ls)

writeFlictLicenseTranslationJSON :: FilePath -> [(LicenseName, License)] -> IO ()
writeFlictLicenseTranslationJSON  outputFolder licenses = let
  flictLicenseTranslation = FlictLicenseTranslation (licensesToTranslations licenses)
  in do
    createDirectoryIfNotExists (outputFolder </> "flict")
    BL.writeFile (outputFolder </> "flict" </> "translation.json") (encodePretty  flictLicenseTranslation)