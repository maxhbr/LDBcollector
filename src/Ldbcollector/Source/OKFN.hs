{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.OKFN
    ( OKFN (..)
    ) where

import qualified Data.Map           as Map
import qualified Data.Vector        as V
import           Ldbcollector.Model

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
    getImpliedStmts l = maybeToList (fmap LicenseUrl (_url l))
                     ++ [stmt ("status: " ++ _status l)]

newtype OKFN = OKFN FilePath

instance Source OKFN where
    getSource _ = Source "OKFN"
    getFacts (OKFN allJSON) = do
        logFileReadIO allJSON
        decoded <- eitherDecodeFileStrict allJSON :: IO (Either String (Map.Map String OKFNLicense))
        case decoded of
            Left err  -> fail err
            Right mapping -> (return . V.map wrapFact . V.fromList . Map.elems) mapping
