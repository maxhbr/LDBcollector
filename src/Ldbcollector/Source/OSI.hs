{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE RecordWildCards #-}

module Ldbcollector.Source.OSI
  ( OSI (..),
    isOsiApproved,
  )
where

import Control.Monad.Except (ExceptT, runExceptT, throwError)
import Data.Aeson (eitherDecode)
import Data.ByteString.Lazy qualified as BL
import Data.Text qualified as T
import Data.Vector qualified as V
import Ldbcollector.Model
import Network.HTTP.Simple (httpLBS, getResponseBody, getResponseStatusCode, parseRequest, Response)
import Control.Exception (try, SomeException)

isOsiApproved :: Maybe Bool -> LicenseStatement
isOsiApproved (Just True) = LicenseRating $ PositiveLicenseRating (ScopedLicenseTag "OSI" "Approved" NoLicenseTagText)
isOsiApproved (Just False) = LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI" "Rejected" NoLicenseTagText)
isOsiApproved Nothing = LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI" "Not-Approved" NoLicenseTagText)

-- | Represents a license entry from the new OSI API at
--   https://opensource.org/api/license
data OSILinks = OSILinks
  { osiLinksHtml :: Maybe Text
  }
  deriving (Eq, Show, Generic)

instance FromJSON OSILinks where
  parseJSON = withObject "OSILinks" $ \o -> do
    html <- o .:? "html"
    href <- case html of
      Nothing -> pure Nothing
      Just h  -> h .:? "href"
    return $ OSILinks href

instance ToJSON OSILinks where
  toJSON (OSILinks href) = object ["html" .= object ["href" .= href]]

data OSILicenseV2 = OSILicenseV2
  { osiId               :: Text
  , osiName             :: Text
  , osiSpdxId           :: Maybe Text
  , osiApproved         :: Maybe Bool
  , osiKeywords         :: [Text]
  , osiLicenseStewardUrl :: Maybe Text
  , osiLinks            :: Maybe OSILinks
  }
  deriving (Eq, Show, Generic)

instance FromJSON OSILicenseV2 where
  parseJSON = withObject "OSILicenseV2" $ \o -> do
    osiId               <- o .: "id"
    osiName             <- o .: "name"
    osiSpdxId           <- o .:? "spdx_id"
    osiApproved         <- o .:? "approved"
    osiKeywords         <- o .:? "keywords" .!= []
    osiLicenseStewardUrl <- do
      url <- o .:? "license_steward_url"
      return $ case url of
        Just u | not (T.null u) -> Just u
        _                       -> Nothing
    osiLinks            <- o .:? "_links"
    return OSILicenseV2 {..}

instance ToJSON OSILicenseV2

newtype OSILicense
  = OSILicense OSILicenseV2
  deriving (Eq, Show, Generic)

instance ToJSON OSILicense

instance LicenseFactC OSILicense where
  getType _ = "OSILicense"
  getApplicableLNs (OSILicense l) =
    LN (newNLN "osi" (osiId l))
      `AlternativeLNs` ( LN (newLN (osiName l))
                           : maybe [] (\s -> [LN (newNLN "SPDX" s)]) (osiSpdxId l)
                       )
  getImpliedStmts (OSILicense l) =
    let approvalStmt = isOsiApproved (osiApproved l)
        stewardUrl   = maybe [] (\u -> [LicenseUrl (Just "License Steward") (T.unpack u)]) (osiLicenseStewardUrl l)
        htmlUrl      = maybe [] (\u -> [LicenseUrl (Just "OSI Page") (T.unpack u)])
                         (osiLinks l >>= osiLinksHtml)
        keywords     = map keywordToStmt (osiKeywords l)
     in [approvalStmt] ++ stewardUrl ++ htmlUrl ++ keywords

keywordToStmt :: Text -> LicenseStatement
keywordToStmt kw = case kw of
  "popular-strong-community"  -> LicenseRating $ PositiveLicenseRating  (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "redundant-with-more-popular" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "voluntarily-retired"       -> LicenseRating $ NegativeLicenseRating  (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "superseded"                -> LicenseRating $ NegativeLicenseRating  (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "non-reusable"              -> LicenseRating $ NegativeLicenseRating  (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "special-purpose"           -> LicenseRating $ NeutralLicenseRating   (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "other-miscellaneous"       -> LicenseRating $ NeutralLicenseRating   (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "international"             -> LicenseRating $ NeutralLicenseRating   (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "uncategorized"             -> LicenseRating $ NeutralLicenseRating   (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  _                           -> stmt (T.unpack kw)

data OSI = OSI

instance HasOriginalData OSI where
  getOriginalData OSI =
    FromUrl "https://opensource.org/licenses/" $
      FromUrl "https://opensource.org/api/license"
        NoPreservedOriginalData

instance Source OSI where
  getSource _ = Source "OSI"
  guardSource _ = lift $ do
    request <- parseRequest "https://opensource.org/api/license"
    result  <- try (httpLBS request) :: IO (Either SomeException (Response BL.ByteString))
    case result of
      Left _  -> do
        errorM rootLoggerName "OSI API is not accessible"
        return False
      Right r -> return (getResponseStatusCode r == 200)
  getFacts OSI = do
    response <- runExceptT fetchLicenses
    case response of
      Left err -> do
        stderrLogIO $ "Error: " ++ err
        pure mempty
      Right licenses ->
        (return . V.fromList . map (wrapFact . OSILicense)) licenses

fetchLicenses :: ExceptT String IO [OSILicenseV2]
fetchLicenses = do
  request  <- lift $ parseRequest "https://opensource.org/api/license"
  result   <- lift $ (try (httpLBS request) :: IO (Either SomeException (Response BL.ByteString)))
  response <- either (throwError . show) return result
  let body = getResponseBody response
  either throwError return (eitherDecode body)
