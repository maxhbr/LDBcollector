{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.Fossology
    ( Fossology (..)
    ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Data.Vector as V

data FossologyEntry
    = FossologyEntry
    { _rf_shortname :: LicenseName
    , _rf_text :: Text
    , _rf_url :: Maybe String
    , _rf_add_date :: Maybe String
    , _rf_copyleft :: Maybe Bool
    , _rf_OSIapproved :: Maybe Bool
    , _rf_fullname :: LicenseName
    , _rf_FSFfree :: Maybe Bool
    , _rf_GPLv2compatible :: Maybe Bool
    , _rf_GPLv3compatible :: Maybe Bool
    , _rf_notes :: Maybe Text
    , _rf_Fedora :: Maybe LicenseName
    , _marydone :: Bool
    , _rf_active :: Bool
    , _rf_text_updatable :: Bool
    -- , _rf_detector_type :: Int
    , _rf_source :: Maybe String
    , _rf_risk :: Maybe String
    , _rf_spdx_compatible :: Bool
    -- , _rf_flag :: Int
    } deriving (Show, Eq, Ord, Generic)
instance FromJSON FossologyEntry where
  parseJSON = let
        toBool :: String -> Bool
        toBool "t" = True
        toBool "f" = False
        toBool _ = False
    in withObject "FossologyEntry" $ \v -> FossologyEntry
        <$> (newNLN "fossology" <$> v .: "rf_shortname")
        <*> v .: "rf_text"
        <*> v .:? "rf_url"
        <*> v .:? "rf_add_date"
        <*> (fmap toBool <$> v .:? "rf_copyleft")
        <*> (fmap toBool <$> v .:? "rf_OSIapproved")
        <*> v .: "rf_fullname"
        <*> (fmap toBool <$> v .:? "rf_FSFfree")
        <*> (fmap toBool <$> v .:? "rf_GPLv2compatible")
        <*> (fmap toBool <$> v .:? "rf_GPLv3compatible")
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

instance LicenseFactC FossologyEntry where
    getType _ = "Fossology"
    getApplicableLNs entry =
        LN (_rf_shortname entry) `AlternativeLNs` map LN (_rf_fullname entry : maybeToList (_rf_Fedora entry))
    getImpliedStmts entry =
        [ MaybeStatement (fmap LicenseUrl (_rf_url entry))
        , MaybeStatement (fmap LicenseComment (_rf_notes entry))
        , LicenseText (_rf_text entry)
        , case _rf_copyleft entry of
            Just True -> typestmt "Copyleft"
            Just False -> typestmt "Permissive"
            _ -> MaybeStatement Nothing
        , MaybeStatement (fmap (ifToStmt "OSIapproved") (_rf_OSIapproved entry))
        , MaybeStatement (fmap (ifToStmt "FSFfree") (_rf_FSFfree entry))
        , MaybeStatement (fmap (ifToStmt "GPLv2compatible") (_rf_GPLv2compatible entry))
        , MaybeStatement (fmap (ifToStmt "GPLv3compatible") (_rf_GPLv3compatible entry))
        ]




-- applyFossologyLicenseRef :: FossologyEntry -> LicenseGraphTask
-- applyFossologyLicenseRef entry = 
--     EdgeLeft (AddTs . V.fromList $
--          [ maybeToTask fromString  (_rf_url entry)
--          ]) AppliesTo $
--     EdgeLeft (Adds . V.fromList $
--          [ (LicenseName . fromString . _rf_fullname) entry
--          ]) Same $
--     fromValue entry (LicenseName . fromString . _rf_shortname) (const Nothing)

newtype Fossology = FossologyLicenseRef FilePath
instance Source Fossology where
    getOrigin _ = Origin "Fossology"
    getFacts (FossologyLicenseRef json) = do
        logFileReadIO json
        decoded <- eitherDecodeFileStrict json :: IO (Either String [FossologyEntry])
        case decoded of
            Left err           -> fail err
            Right fossologyData -> (return . V.fromList . map wrapFact) fossologyData
