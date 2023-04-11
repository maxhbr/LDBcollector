{-# LANGUAGE DeriveAnyClass    #-}
{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.EclipseOrgLegal
    ( EclipseOrgLegal (..)
    ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Data.Vector           as V
import qualified Data.Map as Map

data EclipseOrgLegalLicense
    = ApprovedLicense LicenseName LicenseName
    | RestrictedLicense LicenseName LicenseName
    deriving (Show, Ord, Eq, Generic, ToJSON)

instance LicenseFactC EclipseOrgLegalLicense where
    getType _ = "EclipseLicense"
    getApplicableLNs (ApprovedLicense shortName longName) = LN shortName `AlternativeLNs` [LN longName]
    getApplicableLNs (RestrictedLicense shortName longName) = LN shortName `AlternativeLNs` [LN longName]
    getImpliedStmts (ApprovedLicense _ _) = [stmt "Eclipse: Approved"]
    getImpliedStmts (RestrictedLicense _ _) = [stmt "Eclipse: Restricted"]


data EclipseOrgLegalLicensesJson
    = EclipseOrgLegalLicensesJson (Map.Map Text Text) (Map.Map Text Text)
instance FromJSON EclipseOrgLegalLicensesJson where
  parseJSON = withObject "EclipseOrgLegalLicensesJson" $ \v -> EclipseOrgLegalLicensesJson
    <$> v .: "approved"
    <*> v .: "restricted"
jsonToLicenses :: EclipseOrgLegalLicensesJson -> V.Vector EclipseOrgLegalLicense
jsonToLicenses (EclipseOrgLegalLicensesJson approved restricted) = let
        entryToLicense :: (LicenseName -> LicenseName -> EclipseOrgLegalLicense) -> (Text,Text) -> EclipseOrgLegalLicense
        entryToLicense c (shortName,longName) = c (newNLN "eclipse" shortName) (newLN longName)
        approvedLicenses = map (entryToLicense ApprovedLicense) (Map.assocs approved)
        restrictedLicenses = map (entryToLicense RestrictedLicense) (Map.assocs restricted)
    in V.fromList $ approvedLicenses <> restrictedLicenses


newtype EclipseOrgLegal = EclipseOrgLegal FilePath
instance Source EclipseOrgLegal where
    getSource _  = Source "Eclipse"
    getFacts (EclipseOrgLegal json) = do
        decoded <- eitherDecodeFileStrict json :: IO (Either String EclipseOrgLegalLicensesJson)
        case decoded of
            Left err     -> fail err
            Right result -> return (V.map wrapFact (jsonToLicenses result))

