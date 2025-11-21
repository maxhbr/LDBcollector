{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE RecordWildCards #-}

module Ldbcollector.Source.OpenSourceOrg
  ( OpenSourceOrgLicenses (..),
  )
where

import Data.Text qualified as T
import Data.Vector qualified as V
import Ldbcollector.Model
import Ldbcollector.Source.OSI (isOsiApproved)

newtype OpenSourceIdentifier = OpenSourceIdentifier
  { osiIdentifier :: LicenseName
  }
  deriving (Show, Eq, Generic)

instance FromJSON OpenSourceIdentifier where
  parseJSON = withObject "OpenSourceIdentifier" $ \o -> do
    identifier <- o .: "identifier"
    scheme <- o .: "scheme"
    return . OpenSourceIdentifier . newNLN scheme $ identifier

newtype OpenSourceLink = OpenSourceLink (Maybe String, String)
  deriving (Show, Eq, Generic)

instance FromJSON OpenSourceLink where
  parseJSON = withObject "OpenSourceLink" $ \o -> do
    note <- o .:? "note"
    url <- o .: "url"
    return . OpenSourceLink $ (fmap T.unpack note, T.unpack url)

data OpenSourceTextLink = OpenSourceTextLink
  { otlTitle :: Maybe String,
    otlUrl :: String
  }
  deriving (Show, Eq, Generic)

instance FromJSON OpenSourceTextLink where
  parseJSON = withObject "OpenSourceTextLink" $ \o -> do
    title <- o .:? "title"
    url <- o .: "url"
    return $
      OpenSourceTextLink
        { otlTitle = fmap T.unpack title,
          otlUrl = T.unpack url
        }

data OpenSourceOtherName = OpenSourceOtherName
  { soonName :: LicenseName,
    soonNote :: Maybe String
  }
  deriving (Show, Eq, Generic)

instance FromJSON OpenSourceOtherName where
  parseJSON = \case
    String txt ->
      return $
        OpenSourceOtherName
          { soonName = newLN txt,
            soonNote = Nothing
          }
    value ->
      withObject "OpenSourceOtherName"
        ( \o -> do
            name <- newLN <$> o .: "name"
            note <- fmap T.unpack <$> o .:? "note"
            return $
              OpenSourceOtherName
                { soonName = name,
                  soonNote = note
                }
        )
        value

instance ToJSON OpenSourceOtherName where
  toJSON OpenSourceOtherName {..} =
    case soonNote of
      Nothing -> String (licenseNameToText soonName)
      Just note ->
        object
          [ "name" .= licenseNameToText soonName,
            "note" .= note
          ]

data OpenSourceOrgLicense = OpenSourceOrgLicense
  { osolId :: LicenseName,
    osolName :: LicenseName,
    osolIdentifiers :: [OpenSourceIdentifier],
    osolOtherNames :: [OpenSourceOtherName],
    osolKeywords :: [Text],
    osolLinks :: [OpenSourceLink],
    osolTexts :: [OpenSourceTextLink],
    osolSupersededBy :: Maybe LicenseName
  }
  deriving (Show, Eq, Generic)

instance FromJSON OpenSourceOrgLicense where
  parseJSON = withObject "OpenSourceOrgLicense" $ \o -> do
    osolId <- newNLN "osi" <$> o .: "id"
    osolName <- newLN <$> o .: "name"
    osolIdentifiers <- o .:? "identifiers" .!= []
    osolOtherNames <- o .:? "other_names" .!= []
    osolKeywords <- o .:? "keywords" .!= []
    osolLinks <- o .:? "links" .!= []
    osolTexts <- o .:? "text" .!= []
    osolSupersededBy <- fmap (newNLN "osi") <$> o .:? "superseded_by"
    return OpenSourceOrgLicense {..}

newtype OpenSourceOrgFact
  = OpenSourceOrgFact OpenSourceOrgLicense
  deriving (Show, Eq, Generic)

instance ToJSON OpenSourceOrgFact where
  toJSON (OpenSourceOrgFact OpenSourceOrgLicense {..}) =
    let toIdentifier (OpenSourceIdentifier ln) = ln
        toLink (OpenSourceLink (note, url)) = object ["note" .= note, "url" .= url]
        toTextLink OpenSourceTextLink {..} = object ["title" .= otlTitle, "url" .= otlUrl]
     in object
          [ "id" .= osolId,
            "name" .= osolName,
            "identifiers" .= map toIdentifier osolIdentifiers,
            "otherNames" .= osolOtherNames,
            "keywords" .= osolKeywords,
            "links" .= map toLink osolLinks,
            "texts" .= map toTextLink osolTexts,
            "supersededBy" .= osolSupersededBy
          ]

keywordToStmt :: Text -> LicenseStatement
keywordToStmt kw = case T.toLower kw of
  "osi-approved" -> isOsiApproved (Just True)
  "discouraged" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "non-reusable" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "retired" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "redundant" -> LicenseRating $ NegativeLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "popular" -> LicenseRating $ PositiveLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  "permissive" -> LicenseType Permissive
  "copyleft" -> LicenseType Copyleft
  "special-purpose" -> LicenseRating $ NeutralLicenseRating (ScopedLicenseTag "OSI-keyword" kw NoLicenseTagText)
  _ -> stmt (T.unpack kw)

instance LicenseFactC OpenSourceOrgFact where
  getType _ = "OpenSourceOrgLicense"
  getApplicableLNs (OpenSourceOrgFact license) =
    let identifiers = map (\(OpenSourceIdentifier ln) -> LN ln) (osolIdentifiers license)
        otherNames = map (LN . soonName) (osolOtherNames license)
     in LN (osolId license)
          `AlternativeLNs` (LN (osolName license) : identifiers)
          `ImpreciseLNs` otherNames
  getImpliedStmts (OpenSourceOrgFact license) =
    let links =
          map
            (\(OpenSourceLink (note, url)) -> LicenseUrl note url)
            (osolLinks license)
        textLinks =
          map
            (\(OpenSourceTextLink title url) -> LicenseUrl title url)
            (osolTexts license)
        keywords = map keywordToStmt (osolKeywords license)
        superseded =
          maybe
            []
            ( \target ->
                [ commentStmt "OSI" ("Superseded by " <> licenseNameToText target),
                  stmt ("SupersededBy:" ++ T.unpack (licenseNameToText target))
                ]
            )
            (osolSupersededBy license)
     in links ++ textLinks ++ keywords ++ superseded

newtype OpenSourceOrgLicenses = OpenSourceOrgLicenses FilePath
  deriving (Show, Generic)

instance HasOriginalData OpenSourceOrgLicenses where
  getOriginalData (OpenSourceOrgLicenses file) =
    FromUrl "https://opensource.org/licenses/" $
      FromUrl "https://github.com/OpenSourceOrg/licenses" $
        FromFile file NoPreservedOriginalData

instance Source OpenSourceOrgLicenses where
  getSource _ = Source "OpenSourceOrgLicenses"
  getExpectedFiles (OpenSourceOrgLicenses file) = [file]
  getFacts (OpenSourceOrgLicenses file) = do
    logFileReadIO file
    decoded <- eitherDecodeFileStrict file :: IO (Either String [OpenSourceOrgLicense])
    case decoded of
      Left err -> fail err
      Right licenses ->
        return . V.fromList . map (wrapFact . OpenSourceOrgFact) $ licenses
