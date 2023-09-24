{-# LANGUAGE DeriveAnyClass #-}
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Source.EclipseOrgLegal
  ( EclipseOrgLegal (..),
  )
where

import Data.Map qualified as Map
import Data.Vector qualified as V
import Ldbcollector.Model hiding (ByteString)

data EclipseOrgLegalLicense
  = ApprovedLicense LicenseName LicenseName
  | RestrictedLicense LicenseName LicenseName
  deriving (Show, Ord, Eq, Generic, ToJSON)

instance LicenseFactC EclipseOrgLegalLicense where
  getType _ = "EclipseLicense"
  getApplicableLNs (ApprovedLicense shortName longName) = LN shortName `AlternativeLNs` [LN longName]
  getApplicableLNs (RestrictedLicense shortName longName) = LN shortName `AlternativeLNs` [LN longName]
  getImpliedStmts a@(ApprovedLicense _ _) =
    let desc = "This approved license list enumerates the licenses that the Eclipse Foundation has approved for third-party content used by its projects. Inclusion in this list does not imply that the Eclipse Foundation has determined that every one of these licenses can be used by your Eclipse Foundation project. That is, the licenses on this list are not necessarily compatible with every Eclipse Foundation project license, or with each other. "
     in [LicenseRating (PositiveLicenseRating (getType a) "Approved" (Just desc))]
  getImpliedStmts a@(RestrictedLicense _ _) = [LicenseRating (NegativeLicenseRating (getType a) "Restricted" Nothing)]

data EclipseOrgLegalLicensesJson
  = EclipseOrgLegalLicensesJson (Map.Map Text Text) (Map.Map Text Text)

instance FromJSON EclipseOrgLegalLicensesJson where
  parseJSON = withObject "EclipseOrgLegalLicensesJson" $ \v ->
    EclipseOrgLegalLicensesJson
      <$> v .: "approved"
      <*> v .: "restricted"

jsonToLicenses :: EclipseOrgLegalLicensesJson -> V.Vector EclipseOrgLegalLicense
jsonToLicenses (EclipseOrgLegalLicensesJson approved restricted) =
  let entryToLicense :: (LicenseName -> LicenseName -> EclipseOrgLegalLicense) -> (Text, Text) -> EclipseOrgLegalLicense
      entryToLicense c (shortName, longName) = c (newNLN "eclipse" shortName) (newLN longName)
      approvedLicenses = map (entryToLicense ApprovedLicense) (Map.assocs approved)
      restrictedLicenses = map (entryToLicense RestrictedLicense) (Map.assocs restricted)
   in V.fromList $ approvedLicenses <> restrictedLicenses

newtype EclipseOrgLegal = EclipseOrgLegal FilePath

instance HasOriginalData EclipseOrgLegal where
  getOriginalData (EclipseOrgLegal json) =
    FromUrl "https://www.eclipse.org/legal/licenses.json" $
      FromFile json NoPreservedOriginalData

instance Source EclipseOrgLegal where
  getSource _ = Source "Eclipse"
  getFacts (EclipseOrgLegal json) = do
    decoded <- eitherDecodeFileStrict json :: IO (Either String EclipseOrgLegalLicensesJson)
    case decoded of
      Left err -> fail err
      Right result -> return (V.map wrapFact (jsonToLicenses result))
