{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.Fedora
    ( FedoraLicenseData (..)
    ) where

import Ldbcollector.Model hiding (ByteString) 

import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.Vector as V
import qualified Data.Map as Map
import qualified Data.ByteString.Char8 as Char8
import qualified Control.Monad.State as MTL

data FedoraEntryLicense
    = FedoraEntryLicense
    { _expression :: String
    , _status :: [String]
    , _urls :: [String]
    , _text :: Maybe String
    , _scancode_key :: Maybe String
    }
instance FromJSON FedoraEntryLicense where
  parseJSON = withObject "FedoraEntryLicense" $ \v -> FedoraEntryLicense
    <$> v .: "expression"
    <*> v .: "status"
    <*> v .: "urls"
    <*> v .: "text"
    <*> v .:? "scancode-key"
data FedoraEntryFedora
    = FedoraEntryFedora
    { _legacy_names :: [String]
    , _legacy_abbreviation :: [String]
    , _notes :: Maybe String
    }
instance FromJSON FedoraEntryFedora where
  parseJSON = withObject "FedoraEntryFedora" $ \v -> FedoraEntryFedora
    <$> v .: "legacy-names"
    <*> v .: "legacy-abbreviation"
    <*> v .:? "notes"
data FedoraEntry
    = FedoraEntry
    { _license :: FedoraEntryLicense
    , _fedora :: Maybe FedoraEntryFedora
    }
instance FromJSON FedoraEntry where
  parseJSON = withObject "FedoraEntry" $ \v -> FedoraEntry
    <$> v .: "license"
    <*> v .:? "fedora"

applyFedoraEntry :: FedoraEntry -> LicenseGraphM ()
applyFedoraEntry = undefined

applyJson :: FilePath -> LicenseGraphM ()
applyJson json = do
    stderrLog ("read " ++ json)
    decoded <- MTL.lift (eitherDecodeFileStrict json :: IO (Either String FedoraEntry))
    case decoded of
      Left err -> fail err
      Right entry -> applyFedoraEntry entry

newtype FedoraLicenseData = FedoraLicenseData FilePath
instance Source FedoraLicenseData where
    applySource (FedoraLicenseData dir) = do
        stderrLog ("read " ++ dir)
        jsons <- MTL.lift $ glob (dir </> "*.json")
        mapM_ applyJson jsons