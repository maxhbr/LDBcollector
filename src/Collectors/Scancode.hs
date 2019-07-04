{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TupleSections #-}
module Collectors.Scancode
  ( loadScancodeFacts
  , scancodeLFC
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id, ByteString)
import           Collectors.Common

import qualified Data.Vector as V
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8
import           Data.Yaml
import           Data.Text.Encoding (decodeUtf8)

import           Model.License

-- loadScancodeFactsFromString

{-

key: mit
short_name: MIT License
name: MIT License
category: Permissive
owner: MIT
homepage_url: http://opensource.org/licenses/mit-license.php
notes: Per SPDX.org, this license is OSI certified.
spdx_license_key: MIT
text_urls:
    - http://opensource.org/licenses/mit-license.php
osi_url: http://www.opensource.org/licenses/MIT
other_urls:
    - https://opensource.org/licenses/MIT

-}

data ScancodeData
  = ScancodeData
  { key :: !String
  , shortName :: !String
  , name :: !String
  , category :: Maybe String
  , spdxId :: Maybe String
  , owner :: Maybe String
  , homepageUrl :: Maybe String
  , textUrls :: Maybe [String]
  , osiUrl :: Maybe String
  , otherUrls :: Maybe [String]
  , text :: !ByteString
  } deriving (Show, Generic)
instance ToJSON ByteString where
  toJSON = toJSON . Char8.unpack
instance FromJSON ScancodeData where
  parseJSON = withObject "ScancodeData" $ \v -> ScancodeData
    <$> v .: "key"
    <*> v .: "short_name"
    <*> v .: "name"
    <*> v .:? "category"
    <*> v .:? "spdx_license_key"
    <*> v .:? "owner"
    <*> v .:? "homepage_url"
    <*> v .:? "etxt_urls"
    <*> v .:? "osi_url"
    <*> v .:? "other_urls"
    <*> pure "" -- LicenseText is added later
instance ToJSON ScancodeData
scancodeLFC :: LicenseFactClassifier
scancodeLFC = LFC "Scancode"
instance LFRaw ScancodeData where
  getLicenseFactClassifier _                            = scancodeLFC
  getImpliedNames scd@ScancodeData{key=k, shortName=sn} = CLSR $ [k,sn] ++ (case spdxId scd of
                                                                              Just sid -> [sid]
                                                                              Nothing  -> [])
  getImpliedId scd@ScancodeData{spdxId=mi} = case mi of
    Just i -> mkRLSR scd 90 i
    Nothing -> NoRLSR
  getImpliedText scd = mkRLSR scd 50 (decodeUtf8 $ text scd)
  getImpliedURLs scd = let
      urlsFromHomepage = case homepageUrl scd of
        Just homepageU -> [(Just "Homepage", homepageU)]
        Nothing -> []
      urlsForText = case textUrls scd of
        Just textUs -> map (Just "Text",) textUs
        Nothing -> []
      urlsFromOsi = case osiUrl scd of
        Just osiU -> [(Just "OSI Page", osiU)]
        Nothing -> []
      urlsFromOther = case otherUrls scd of
        Just otherUs -> map (Nothing,) otherUs
        Nothing -> []
    in CLSR $ urlsFromHomepage ++ urlsForText ++ urlsFromOsi ++ urlsFromOther
  getImpliedCopyleft scd@ScancodeData{category=Nothing} = NoSLSR
  getImpliedCopyleft scd@ScancodeData{category=Just c}  = case c of
    "Hardware License" -> NoSLSR
    "Patent License" -> NoSLSR
    "Unstated License" -> NoSLSR
    "Free Restricted" -> NoSLSR
    "Proprietary Free" -> NoSLSR
    _ -> SLSR (getLicenseFactClassifier scd) $ case c of
          "Copyleft" -> Copyleft
          "Copyleft Limited" -> WeakCopyleft
          "Permissive" -> NoCopyleft
          "Commercial" -> NoCopyleft
          "Public Domain" -> NoCopyleft
          _ -> undefined -- TODO?

loadScancodeFactsFromYml :: FilePath -> FilePath -> IO Facts
loadScancodeFactsFromYml folder yml = let
    ymlFile = folder </> yml
    licenseFile = replaceExtension ymlFile "LICENSE"
  in do
    decoded <- decodeFileEither ymlFile :: IO (Either ParseException ScancodeData)

    licenseTextExists <- doesFileExist licenseFile
    licenseText <- if licenseTextExists
      then B.readFile licenseFile
      else return ""
    return $ case decoded of
      Left pe -> trace (show pe) V.empty
      Right scdFromRow -> let
          scd = scdFromRow{text = licenseText}
        in V.singleton (LicenseFact (Just $ "https://github.com/nexB/scancode-toolkit/blob/develop/src/licensedcode/data/licenses/" ++ yml) scd)

loadScancodeFacts :: FilePath -> IO Facts
loadScancodeFacts folder = do
  logThatFactsAreLoadedFrom "Scancode License List"
  files <- getDirectoryContents folder
  let ymls = filter ("yml" `isSuffixOf`) files
  factss <- mapM (loadScancodeFactsFromYml folder) ymls
  let facts = foldl (V.++) V.empty factss
  return facts