{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.Scancode
  ( ScancodeLicenseDB (..)
  ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Control.Monad.State   as MTL
import           Data.ByteString       (ByteString)
import qualified Data.ByteString       as B
import qualified Data.ByteString.Char8 as Char8
import qualified Data.Map              as Map
import qualified Data.Vector           as V

data ScancodeData
  = ScancodeData
  { _key         :: !String
  , _shortName   :: !String
  , _name        :: !String
  , _category    :: Maybe String
  , _spdxId      :: Maybe String
  , _owner       :: Maybe String
  , _homepageUrl :: Maybe String
  , _notes       :: Maybe String
  , _textUrls    :: Maybe [String]
  , _osiUrl      :: Maybe String
  , _otherUrls   :: Maybe [String]
  , _text        :: Maybe Text
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

applyScancodeData :: ScancodeData -> LicenseGraphTask
applyScancodeData scd = let
        shortname = Add $ LicenseName (newLN (pack (_shortName scd)))
        name = Add $ LicenseName (newLN (pack (_name scd)))
    in
      EdgeLeft (
            AddTs (V.fromList
                [ maybeToTask fromString (_category scd)
            ])
       ) AppliesTo $
      EdgeLeft (
            AddTs (V.fromList
                [ shortname
                , name
            ])
       ) Better $
          fromValue scd
              (LicenseName . newNLN "scancode" . pack . _key)
              (fmap (LicenseName . newNLN "SPDX" . pack) . _spdxId)

applyJson :: FilePath -> IO LicenseGraphTask
applyJson json = do
    putStrLn ("read " ++ json)
    decoded <- eitherDecodeFileStrict json :: IO (Either String ScancodeData)
    case decoded of
      Left err           -> fail err
      Right scancodeData -> return $ applyScancodeData scancodeData

instance Source ScancodeLicenseDB where
    getTask (ScancodeLicenseDB dir) = do
        scancodeJsons <- (fmap (filter (not . isSuffixOf "index.json")) . glob) (dir </> "*.json")
        AddTs . V.fromList <$> mapM applyJson scancodeJsons
