{-# LANGUAGE DeriveAnyClass    #-}
{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.EclipseOrgLegal
    ( EclipseOrgLegal (..)
    ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Data.Vector           as V

data EclipseOrgLegalEntryLicense
    = EclipseOrgLegalEntryLicense
    { _expression   :: LicenseName
    , _status       :: [String]
    , _urls         :: [String]
    , _text         :: Maybe Text
    , _scancode_key :: Maybe LicenseName
    }
    deriving (Show, Ord, Eq, Generic, ToJSON)
instance FromJSON EclipseOrgLegalEntryLicense where
  parseJSON = withObject "EclipseOrgLegalEntryLicense" $ \v -> EclipseOrgLegalEntryLicense
    <$> (newNLN "spdx" <$> v .: "expression")
    <*> v .: "status"
    <*> (fmap lines <$> (v .:? "url")) .!= []
    <*> v .:? "text"
    <*> (fmap (newNLN "scancode") <$> v .:? "scancode-key")
data EclipseOrgLegalEntryEclipseOrgLegal
    = EclipseOrgLegalEntryEclipseOrgLegal
    { _legacy_names        :: [LicenseName]
    , _legacy_abbreviation :: [LicenseName]
    , _notes               :: Maybe Text
    }
    deriving (Show, Ord, Eq, Generic, ToJSON)
instance FromJSON EclipseOrgLegalEntryEclipseOrgLegal where
  parseJSON = withObject "EclipseOrgLegalEntryEclipseOrgLegal" $ \v -> EclipseOrgLegalEntryEclipseOrgLegal
    <$> v .:? "legacy-name" .!= []
    <*> v .:? "legacy-abbreviation" .!= []
    <*> v .:? "notes"
data EclipseOrgLegalEntry
    = EclipseOrgLegalEntry
    { _id :: Maybe String
    , _license :: EclipseOrgLegalEntryLicense
    , _fedora  :: EclipseOrgLegalEntryEclipseOrgLegal
    }
    deriving (Show, Ord, Eq, Generic, ToJSON)
instance FromJSON EclipseOrgLegalEntry where
  parseJSON = withObject "EclipseOrgLegalEntry" $ \v -> EclipseOrgLegalEntry
    <$> pure Nothing
    <*> v .: "license"
    <*> v .:? "fedora" .!= EclipseOrgLegalEntryEclipseOrgLegal [] [] Nothing

instance LicenseFactC EclipseOrgLegalEntry where
    getType _ = "EclipseOrgLegalEntry"
    getApplicableLNs (EclipseOrgLegalEntry (Just id) (EclipseOrgLegalEntryLicense {_expression = expression, _scancode_key = scancode_key}) (EclipseOrgLegalEntryEclipseOrgLegal { _legacy_names = legacy_names , _legacy_abbreviation = legacy_abbreviation})) =
        (LN . newNLN "EclipseOrgLegal" . pack) id `AlternativeLNs` map LN (expression : maybeToList scancode_key)
             `ImpreciseLNs` map LN (legacy_names ++ legacy_abbreviation)
    getApplicableLNs _ = undefined -- should not happen
    getImpliedStmts (EclipseOrgLegalEntry _ (EclipseOrgLegalEntryLicense { _status = status , _urls = urls , _text = text }) (EclipseOrgLegalEntryEclipseOrgLegal {_notes = notes})) =
        [ stmt (show status)
        ]
        ++ map LicenseUrl urls
        ++ map LicenseText (maybeToList text)
        ++ map LicenseText (maybeToList notes)

getEntry :: FilePath -> IO EclipseOrgLegalEntry
getEntry json = do
    logFileReadIO json
    let id = takeBaseName (takeBaseName json)
    decoded <- eitherDecodeFileStrict json :: IO (Either String EclipseOrgLegalEntry)
    case decoded of
      Left err    -> fail err
      Right entry -> return $ entry{ _id = Just id }

newtype EclipseOrgLegal = EclipseOrgLegal FilePath
instance Source EclipseOrgLegal where
    getOrigin _  = Origin "eclipse.org/legal/licenses.json"
    getFacts (EclipseOrgLegal json) = do
        decoded <- eitherDecodeFileStrict json :: IO (Either String EclipseOrgLegalEntry)
        case decoded of
            Left err     -> fail err
            Right result -> undefined

