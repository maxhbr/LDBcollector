{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.Fossology
    ( Fossology (..)
    ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Data.Vector as V

data FossologyEntry
    = FossologyEntry
    { _rf_shortname :: String
    , _rf_text :: Text
    , _rf_url :: Maybe String
    , _rf_add_date :: Maybe String
    , _rf_copyleft :: Maybe String
    , _rf_OSIapproved :: Maybe String
    , _rf_fullname :: String
    , _rf_FSFfree :: Maybe String
    , _rf_GPLv2compatible :: Maybe String
    , _rf_GPLv3compatible :: Maybe String
    , _rf_notes :: Maybe Text
    , _rf_Fedora :: Maybe String
    , _marydone :: Bool
    , _rf_active :: Bool
    , _rf_text_updatable :: Bool
    -- , _rf_detector_type :: Int
    , _rf_source :: Maybe String
    , _rf_risk :: Maybe String
    , _rf_spdx_compatible :: Bool
    -- , _rf_flag :: Int
    } deriving (Show, Generic)
instance FromJSON FossologyEntry where
  parseJSON = let
        toBool :: String -> Bool
        toBool "t" = True
        toBool "f" = False
        toBool _ = False
    in withObject "FossologyEntry" $ \v -> FossologyEntry
        <$> v .: "rf_shortname"
        <*> v .: "rf_text"
        <*> v .:? "rf_url"
        <*> v .:? "rf_add_date"
        <*> v .:? "rf_copyleft"
        <*> v .:? "rf_OSIapproved"
        <*> v .: "rf_fullname"
        <*> v .:? "rf_FSFfree"
        <*> v .:? "rf_GPLv2compatible"
        <*> v .:? "rf_GPLv3compatible"
        <*> v .:? "rf_notes"
        <*> v .:? "rf_Fedora"
        <*> (toBool <$> v .: "marydone")
        <*> (toBool <$> v .: "rf_active")
        <*> (toBool <$> v .: "rf_text_updatable")
        -- <*> v .: "rf_detector_type"
        <*> v .:? "rf_source"
        <*> v .:? "rf_risk"
        <*> (toBool <$> v .: "rf_spdx_compatible")
        -- <*> v .: "rf_flag"
instance ToJSON FossologyEntry

applyFossologyLicenseRef :: FossologyEntry -> LicenseGraphTask
applyFossologyLicenseRef entry = 
    EdgeLeft (AddTs . V.fromList $
         [ maybeToTask fromString  (_rf_url entry)
         ]) AppliesTo $
    EdgeLeft (Adds . V.fromList $
         [ (LicenseName . fromString . _rf_fullname) entry
         ]) Same $
    fromValue entry (LicenseName . fromString . _rf_shortname) (const Nothing)

newtype Fossology = FossologyLicenseRef FilePath
instance Source Fossology where
    getTask (FossologyLicenseRef json) = do
        putStrLn ("read " ++ json)
        decoded <- eitherDecodeFileStrict json :: IO (Either String [FossologyEntry])
        case decoded of
            Left err           -> fail err
            Right scancodeData -> (return . AddTs . V.fromList . map applyFossologyLicenseRef) scancodeData
