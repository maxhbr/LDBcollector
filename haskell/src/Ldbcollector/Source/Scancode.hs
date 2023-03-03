{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TupleSections #-}
{-# LANGUAGE TemplateHaskell #-}
module Ldbcollector.Source.Scancode
  ( ScancodeLicenseDB (..)
  ) where

import Ldbcollector.Model hiding (ByteString) 

import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.Vector as V
import qualified Data.Map as Map
import qualified Data.ByteString.Char8 as Char8
import qualified Control.Monad.State as MTL

data ScancodeData
  = ScancodeData
  { _key :: !String
  , _shortName :: !String
  , _name :: !String
  , _category :: Maybe String
  , _spdxId :: Maybe String
  , _owner :: Maybe String
  , _homepageUrl :: Maybe String
  , _notes :: Maybe String
  , _textUrls :: Maybe [String]
  , _osiUrl :: Maybe String
  , _otherUrls :: Maybe [String]
  , _text :: Maybe Text
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
    <*> v .:? "notes"
    <*> v .:? "text_urls"
    <*> v .:? "osi_url"
    <*> v .:? "other_urls"
    <*> v .:? "text"
instance ToJSON ScancodeData

newtype ScancodeLicenseDB = ScancodeLicenseDB FilePath

-- loadScancodeFactsFromData :: (FilePath, ByteString, Maybe ByteString) -> ScancodeData
-- loadScancodeFactsFromData (fn, yml, licText) = let
--     decoded = decodeEither' yml :: (Either ParseException ScancodeData)
--   in case decoded of
--       Left pe -> undefined
--       Right scdFromRow -> scdFromRow{text = licText}

applyScancodeData :: ScancodeData -> LicenseGraphM ()
applyScancodeData scd = do
    let value = mkLGValue scd
    addNode value
    let key = LicenseName (newNLN "scancode" (pack (_key scd)))
    addEdge (value, key, AppliesTo)

    let shortname = LicenseName (newLN (pack (_shortName scd)))
    addEdge (shortname, key, Same)

    let name = LicenseName (newLN (pack (_name scd)))
    addEdge (name, key, Same)

    case _spdxId scd of
      Just spdxid -> do 
        addEdge (key, LicenseName (newNLN "SPDX" (pack spdxid)), Better)
        return ()
      Nothing -> return ()

    case _category scd of
      Just category -> do
        addEdge (fromString category, key, AppliesTo)
        return ()
      Nothing -> return ()

    return ()

applyJson :: FilePath -> LicenseGraphM ()
applyJson json = do
    decoded <- MTL.lift (eitherDecodeFileStrict json :: IO (Either String ScancodeData))
    case decoded of
      Left err -> fail err
      Right scancodeData -> applyScancodeData scancodeData

instance Source ScancodeLicenseDB where
    applySource (ScancodeLicenseDB dir) = do
        scancodeJsons <- (MTL.lift . fmap (filter (not . isSuffixOf "index.json")) . glob) (dir </> "*.json")
        mapM_ applyJson scancodeJsons