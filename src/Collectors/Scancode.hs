{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.Scancode
  ( loadScancodeFacts
  -- , loadScancodeFactsFromString
  ) where

import Prelude hiding (id)

import           System.FilePath
import           System.Directory
-- import           Text.JSON
import           Data.List
import qualified Data.Text as T
import qualified Data.Text.IO as T
import qualified Data.Vector as V
import           Debug.Trace (trace)
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8
import Data.Aeson
import GHC.Generics
import Data.Yaml

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
  , category :: !String
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
    <*> v .: "category"
    <*> v .:? "spdx_license_key"
    <*> v .:? "owner"
    <*> v .:? "homepage_url"
    <*> v .:? "etxt_urls"
    <*> v .:? "osi_url"
    <*> v .:? "other_urls"
    <*> pure ""
instance ToJSON ScancodeData
instance LFRaw ScancodeData where
  getImpliedShortnames scd@ScancodeData{key=k, shortName=sn} = [k,sn] ++ (case spdxId scd of
                                                                            Just sid -> [sid]
                                                                            Nothing  -> [])
  getType _                                                  = "ScancodeData"

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
        in V.fromList [mkLicenseFact "Scancode" scd]

loadScancodeFacts :: FilePath -> IO Facts
loadScancodeFacts folder = do
  files <- getDirectoryContents folder
  let ymls = filter ("yml" `isSuffixOf`) files
  factss <- mapM (loadScancodeFactsFromYml folder) ymls
  let facts = foldl (V.++) V.empty factss
  return facts
