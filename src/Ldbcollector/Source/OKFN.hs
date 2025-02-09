{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Source.OKFN
  ( OKFN (..),
  )
where

import Data.Map qualified as Map
import Data.Vector qualified as V
import Ldbcollector.Model
import Ldbcollector.Source.OSI (isOsiApproved)

data OKFNLicense = OKFNLicense
  { _domain_content :: Bool,
    _domain_data :: Bool,
    _domain_software :: Bool,
    _family :: Maybe LicenseName,
    _id :: LicenseName,
    _legacy_ids :: [LicenseName],
    _maintainer :: Maybe String,
    _od_conformance :: String,
    _osd_conformance :: String,
    _status :: String,
    _title :: LicenseName,
    _url :: Maybe String
  }
  deriving (Eq, Ord, Show, Generic)

instance FromJSON OKFNLicense where
  parseJSON = withObject "OKFNLicense" $ \v ->
    OKFNLicense
      <$> v .: "domain_content"
      <*> v .: "domain_data"
      <*> v .: "domain_software"
      <*> ( ( \case
                Just "" -> Nothing
                u -> u
            )
              <$> v .:? "family"
          )
      <*> v .: "id"
      <*> v .:? "legacy_ids" .!= []
      <*> ( ( \case
                Just "" -> Nothing
                u -> u
            )
              <$> v .:? "maintainer"
          )
      <*> v .: "od_conformance"
      <*> v .: "osd_conformance"
      <*> v .: "status"
      <*> v .: "title"
      <*> ( ( \case
                Just "" -> Nothing
                u -> u
            )
              <$> v .:? "url"
          )

instance ToJSON OKFNLicense

instance LicenseFactC OKFNLicense where
  getType _ = "OKFN"
  getApplicableLNs l = LN (_id l) `AlternativeLNs` [LN (_title l)] `ImpreciseLNs` map LN (maybeToList (_family l) ++ _legacy_ids l)
  getImpliedStmts l =
    let statusStmt =
          LicenseRating $
            let status = _status l
                tag = ScopedLicenseTag "OKFN status" (pack status) NoLicenseTagText
             in case status of
                  "approved" -> PositiveLicenseRating tag
                  "active" -> PositiveLicenseRating tag
                  _ -> NegativeLicenseRating tag
        odConfromance =
          LicenseRating $
            let odConfromance = _od_conformance l
             in case odConfromance of
                  "approved" ->
                    let desc = LicenseTagDescription "Open means anyone can freely access, use, modify, and share for any purpose (subject, at most, to requirements that preserve provenance and openness)."
                        tag = ScopedLicenseTag "Open Definition" (pack odConfromance) desc
                     in PositiveLicenseRating tag
                  "rejected" ->
                    let tag = ScopedLicenseTag "Open Definition" (pack odConfromance) NoLicenseTagText
                     in NegativeLicenseRating tag
                  _ ->
                    let tag = ScopedLicenseTag "Open Definition" (pack odConfromance) NoLicenseTagText
                     in NeutralLicenseRating tag
        osdConfromance =
          let osdConfromance = _osd_conformance l
           in case osdConfromance of
                "approved" -> isOsiApproved (Just True)
                "rejected" -> isOsiApproved (Just False)
                _ ->
                  let tag = ScopedLicenseTag "OSD" (pack osdConfromance) NoLicenseTagText
                   in LicenseRating $ NeutralLicenseRating tag
     in maybeToList (fmap (LicenseUrl Nothing) (_url l))
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
  getExpectedFiles (OKFN allJSON) = [allJSON]
  getFacts (OKFN allJSON) = do
    logFileReadIO allJSON
    decoded <- eitherDecodeFileStrict allJSON :: IO (Either String (Map.Map String OKFNLicense))
    case decoded of
      Left err -> fail err
      Right mapping -> (return . V.map wrapFact . V.fromList . Map.elems) mapping
