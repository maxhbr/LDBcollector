{-# LANGUAGE DeriveAnyClass    #-}
{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.Fedora
    ( FedoraLicenseData (..)
    ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Control.Monad.State   as MTL
import           Data.ByteString       (ByteString)
import qualified Data.ByteString       as B
import qualified Data.ByteString.Char8 as Char8
import qualified Data.Map              as Map
import qualified Data.Vector           as V
import           GHC.Generics
import           System.FilePath.Posix (takeBaseName)

data FedoraEntryLicense
    = FedoraEntryLicense
    { _expression   :: String
    , _status       :: [String]
    , _urls         :: [String]
    , _text         :: Maybe String
    , _scancode_key :: Maybe String
    }
    deriving (Show, Generic, ToJSON)
instance FromJSON FedoraEntryLicense where
  parseJSON = withObject "FedoraEntryLicense" $ \v -> FedoraEntryLicense
    <$> v .: "expression"
    <*> v .: "status"
    <*> (fmap lines <$> (v .:? "url")) .!= []
    <*> v .:? "text"
    <*> v .:? "scancode-key"
data FedoraEntryFedora
    = FedoraEntryFedora
    { _legacy_names        :: [String]
    , _legacy_abbreviation :: [String]
    , _notes               :: Maybe String
    }
    deriving (Show, Generic, ToJSON)
instance FromJSON FedoraEntryFedora where
  parseJSON = withObject "FedoraEntryFedora" $ \v -> FedoraEntryFedora
    <$> v .:? "legacy-name" .!= []
    <*> v .:? "legacy-abbreviation" .!= []
    <*> v .:? "notes"
data FedoraEntry
    = FedoraEntry
    { _license :: FedoraEntryLicense
    , _fedora  :: FedoraEntryFedora
    }
    deriving (Show, Generic, ToJSON)
instance FromJSON FedoraEntry where
  parseJSON = withObject "FedoraEntry" $ \v -> FedoraEntry
    <$> v .: "license"
    <*> v .:? "fedora" .!= FedoraEntryFedora [] [] Nothing

applyFedoraEntry :: String -> FedoraEntry -> LicenseGraphTask
applyFedoraEntry id entry@(FedoraEntry fel@(FedoraEntryLicense
            { _expression = expression
            , _status = status
            , _urls = urls
            , _text = text
            , _scancode_key = scancode_key
        }) (FedoraEntryFedora
            { _legacy_names = legacy_names
            , _legacy_abbreviation = legacy_abbreviation
            , _notes = notes
        })) = 
      EdgeLeft ( AddTs $ V.fromList [
                Add $ (Vec . map fromString) status,
                Add $ (Vec . map fromString) urls,
                maybeToTask fromString notes
            ]
       ) AppliesTo $
      EdgeLeft (
            maybeToTask (Add . LicenseName . newNLN "scancode" . pack) scancode_key
       ) Better $
      EdgeLeft (
            Adds (V.fromList ( map (LicenseName . newLN . pack) (legacy_names <> legacy_abbreviation)))
       ) Better $
                fromValue entry
                    (const $ (LicenseName . newNLN "fedora" . pack) id)
                    (Just . LicenseName . newNLN "SPDX" . pack . _expression . _license)


applyJson :: FilePath -> IO LicenseGraphTask
applyJson json = do
    let id = takeBaseName (takeBaseName json)
    -- stderrLog ("read " ++ json ++ " for " ++ id)
    decoded <- eitherDecodeFileStrict json :: IO (Either String FedoraEntry)
    case decoded of
      Left err    -> fail err
      Right entry -> return $ applyFedoraEntry id entry

newtype FedoraLicenseData = FedoraLicenseData FilePath
instance Source FedoraLicenseData where
    getTask (FedoraLicenseData dir) = do
        -- stderrLog ("read " ++ dir)
        jsons <- glob (dir </> "*.json")
        AddTs . V.fromList <$> mapM applyJson jsons
