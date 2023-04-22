{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.OKFN
    ( OKFN (..)
    ) where

import qualified Data.Map           as Map
import qualified Data.Vector        as V
import           Ldbcollector.Model
import Ldbcollector.Source.OSI (isOsiApproved)

data OKFNLicense
    = OKFNLicense
    { _domain_content  :: Bool
    , _domain_data     :: Bool
    , _domain_software :: Bool
    , _family          :: Maybe LicenseName
    , _id              :: LicenseName
    , _legacy_ids      :: [LicenseName]
    , _maintainer      :: Maybe String
    , _od_conformance  :: String
    , _osd_conformance :: String
    , _status          :: String
    , _title           :: LicenseName
    , _url             :: Maybe String
    } deriving (Eq, Ord, Show, Generic)
instance FromJSON OKFNLicense where
    parseJSON = withObject "OKFNLicense" $ \v -> OKFNLicense
        <$> v .: "domain_content"
        <*> v .: "domain_data"
        <*> v .: "domain_software"
        <*> ((\case
                Just "" -> Nothing
                u       -> u) <$> v .:? "family")
        <*> v .: "id"
        <*> v .:? "legacy_ids" .!= []
        <*> ((\case
                Just "" -> Nothing
                u       -> u) <$> v .:? "maintainer")
        <*> v .: "od_conformance"
        <*> v .: "osd_conformance"
        <*> v .: "status"
        <*> v .: "title"
        <*> ((\case
                Just "" -> Nothing
                u       -> u) <$> v .:? "url")
instance ToJSON OKFNLicense
instance LicenseFactC OKFNLicense where
    getType _ = "OKFN"
    getApplicableLNs l = LN (_id l) `AlternativeLNs` [LN (_title l)] `ImpreciseLNs` map LN (maybeToList (_family l) ++ _legacy_ids l)
    getImpliedStmts l = let
            statusStmt = LicenseRating $ let
                    status = _status l
                in case status of
                "approved" -> PositiveLicenseRating "OKFN status" (pack status) Nothing
                "active" -> PositiveLicenseRating "OKFN status" (pack status) Nothing
                _ -> NegativeLicenseRating "OKFN status" (pack status) Nothing
            odConfromance = LicenseRating $ let
                    odConfromance = _od_conformance l
                in case odConfromance of
                    "approved" -> PositiveLicenseRating "Open Definition" (pack odConfromance) (Just "Open means anyone can freely access, use, modify, and share for any purpose (subject, at most, to requirements that preserve provenance and openness).")
                    "rejected" -> NegativeLicenseRating "Open Definition" (pack odConfromance) Nothing
                    _ -> NeutralLicenseRating "Open Definition" (pack odConfromance) Nothing
            osdConfromance = let
                    osdConfromance = _osd_conformance l
                in case osdConfromance of
                    "approved" -> isOsiApproved (Just True)
                    "rejected" -> isOsiApproved (Just False)
                    _ -> LicenseRating $ NeutralLicenseRating "OSI" (pack osdConfromance) Nothing
        in maybeToList (fmap LicenseUrl (_url l))
                     ++ [statusStmt, odConfromance, osdConfromance]

newtype OKFN = OKFN FilePath
instance HasOriginalData OKFN where
    getOriginalData (OKFN allJSON) =
        FromUrl "https://opendefinition.org/licenses/" $
        FromUrl "https://opendefinition.org/licenses/api/" $
        FromUrl "https://github.com/okfn/licenses" $
        FromFile allJSON NoPreservedOriginalData
instance Source OKFN where
    getSource _ = Source "OKFN"
    getFacts (OKFN allJSON) = do
        logFileReadIO allJSON
        decoded <- eitherDecodeFileStrict allJSON :: IO (Either String (Map.Map String OKFNLicense))
        case decoded of
            Left err  -> fail err
            Right mapping -> (return . V.map wrapFact . V.fromList . Map.elems) mapping
