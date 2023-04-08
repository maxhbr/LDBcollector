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
    { _expression   :: LicenseName
    , _status       :: [String]
    , _urls         :: [String]
    , _text         :: Maybe Text
    , _scancode_key :: Maybe LicenseName
    }
    deriving (Show, Ord, Eq, Generic, ToJSON)
instance FromJSON FedoraEntryLicense where
  parseJSON = withObject "FedoraEntryLicense" $ \v -> FedoraEntryLicense
    <$> (newNLN "spdx" <$> v .: "expression")
    <*> v .: "status"
    <*> (fmap lines <$> (v .:? "url")) .!= []
    <*> v .:? "text"
    <*> (fmap (newNLN "scancode") <$> v .:? "scancode-key")
data FedoraEntryFedora
    = FedoraEntryFedora
    { _legacy_names        :: [LicenseName]
    , _legacy_abbreviation :: [LicenseName]
    , _notes               :: Maybe Text
    }
    deriving (Show, Ord, Eq, Generic, ToJSON)
instance FromJSON FedoraEntryFedora where
  parseJSON = withObject "FedoraEntryFedora" $ \v -> FedoraEntryFedora
    <$> v .:? "legacy-name" .!= []
    <*> v .:? "legacy-abbreviation" .!= []
    <*> v .:? "notes"
data FedoraEntry
    = FedoraEntry
    { _id :: Maybe String
    , _license :: FedoraEntryLicense
    , _fedora  :: FedoraEntryFedora
    }
    deriving (Show, Ord, Eq, Generic, ToJSON)
instance FromJSON FedoraEntry where
  parseJSON = withObject "FedoraEntry" $ \v -> FedoraEntry
    <$> pure Nothing
    <*> v .: "license"
    <*> v .:? "fedora" .!= FedoraEntryFedora [] [] Nothing

instance LicenseFactC FedoraEntry where
    getType _ = "FedoraEntry"
    getApplicableLNs (FedoraEntry (Just id) (FedoraEntryLicense {_expression = expression, _scancode_key = scancode_key}) (FedoraEntryFedora { _legacy_names = legacy_names , _legacy_abbreviation = legacy_abbreviation})) =
        (NLN . newNLN "Fedora" . pack) id `AlternativeLNs` map NLN (expression : maybeToList scancode_key)
             `ImpreciseLNs` map LN (legacy_names ++ legacy_abbreviation)
    getApplicableLNs _ = undefined -- should not happen
    getImpliedStmts (FedoraEntry _ (FedoraEntryLicense { _status = status , _urls = urls , _text = text }) (FedoraEntryFedora {_notes = notes})) =
        [ stmt (show status)
        ]
        ++ map LicenseUrl urls
        ++ map LicenseText (maybeToList text)
        ++ map LicenseText (maybeToList notes)

getEntry :: FilePath -> IO FedoraEntry
getEntry json = do
    logFileReadIO json
    let id = takeBaseName (takeBaseName json)
    decoded <- eitherDecodeFileStrict json :: IO (Either String FedoraEntry)
    case decoded of
      Left err    -> fail err
      Right entry -> return $ entry{ _id = Just id }

newtype FedoraLicenseData = FedoraLicenseData FilePath
instance Source FedoraLicenseData where
    getOrigin _  = Origin "Fedora"
    getFacts (FedoraLicenseData dir) = do
        -- stderrLog ("read " ++ dir)
        jsons <- glob (dir </> "*.json")
        V.fromList <$> mapM (fmap wrapFact . getEntry) jsons
