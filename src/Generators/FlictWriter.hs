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

data TranslationMeta
  = TranslationMeta
  { software :: String
  , version :: Maybe String
  , description :: Maybe String
  } deriving (Eq, Show, Generic)
instance ToJSON TranslationMeta where
    toEncoding = genericToEncoding (defaultOptions{omitNothingFields = True})
data Translation
  = Translation
  { spdx_id :: LicenseName 
  , license_expression :: LicenseName
  , comment :: Maybe String
  } deriving (Eq, Show, Generic)
instance ToJSON Translation where
    toEncoding = genericToEncoding (defaultOptions{omitNothingFields = True})
data FlictLicenseTranslation
  = FlictLicenseTranslation
  { translations :: [Translation]
  ,  meta :: TranslationMeta
  } deriving (Eq, Show, Generic)
instance ToJSON FlictLicenseTranslation where
    toEncoding = genericToEncoding defaultOptions

factToTranslations :: LicenseName -> LicenseFact -> [Translation]
factToTranslations ln f = let
  names = getImpliedNonambiguousNames f
  otherNames = filter (/= ln) names
  in map (\on -> Translation ln on Nothing) otherNames

factsToTranslations :: LicenseName -> Facts -> [Translation]
factsToTranslations ln fs = concat . V.toList $ V.map (factToTranslations ln) fs

licenseToTranslations :: LicenseName -> License -> [Translation]
licenseToTranslations ln (License fs) = factsToTranslations ln fs

licensesToTranslations :: [(LicenseName, License)] -> [Translation]
licensesToTranslations [] = []
licensesToTranslations ((ln,l):ls) = licenseToTranslations ln l ++ (licensesToTranslations ls)

writeFlictLicenseTranslationJSON :: FilePath -> [(LicenseName, License)] -> IO ()
writeFlictLicenseTranslationJSON  outputFolder licenses = let
  flictLicenseTranslation = FlictLicenseTranslation (licensesToTranslations licenses) (TranslationMeta "LDBcollector" Nothing Nothing)
  in do
    createDirectoryIfNotExists (outputFolder </> "flict")
    BL.writeFile (outputFolder </> "flict" </> "translation.json") (encodePretty  flictLicenseTranslation)