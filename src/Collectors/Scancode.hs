{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.Scancode
  ( loadScancodeFacts
  -- , loadScancodeFactsFromString
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id, ByteString)

import           System.FilePath
import           System.Directory
import           Data.List
import qualified Data.Vector as V
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8
import           Data.Yaml

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
instance LFRaw ScancodeData where
  getLicenseFactClassifier _                            = LFC ["ScancodeData"]
  getImpliedNames scd@ScancodeData{key=k, shortName=sn} = [k,sn] ++ (case spdxId scd of
                                                                       Just sid -> [sid]
                                                                       Nothing  -> [])

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
        in V.singleton (LicenseFact scd)

loadScancodeFacts :: FilePath -> IO Facts
loadScancodeFacts folder = do
  files <- getDirectoryContents folder
  let ymls = filter ("yml" `isSuffixOf`) files
  factss <- mapM (loadScancodeFactsFromYml folder) ymls
  let facts = foldl (V.++) V.empty factss
  return facts
