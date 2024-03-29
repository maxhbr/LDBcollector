{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Source.Metaeffekt
  ( Metaeffekt (..),
  )
where

import Data.Map qualified as Map
import Data.Text qualified as T
import Data.Vector qualified as V
import Data.Yaml qualified as Y
import Data.Yaml.Internal qualified as Y
import Ldbcollector.Model

data MetaeffektLicense = MetaeffektLicense
  { _canonicalName :: LicenseName,
    _category :: LicenseName,
    _shortName :: Maybe LicenseName,
    _spdxIdentifier :: Maybe LicenseName,
    _openCoDEStatus :: Maybe String,
    _alternativeNames :: [LicenseName],
    _otherIds :: [LicenseName]
  }
  deriving (Eq, Ord, Show, Generic)

isLicenseVariant :: MetaeffektLicense -> Bool
isLicenseVariant l = case _canonicalName l of
  LicenseName _ n ->
    any
      (`T.isInfixOf` n)
      [ "(variant ",
        "; variant "
      ]

instance FromJSON MetaeffektLicense where
  parseJSON = withObject "MetaeffektLicense" $ \v ->
    MetaeffektLicense
      <$> (setNS "metaeffekt" <$> v .: "canonicalName")
      <*> v .: "category"
      <*> (fmap (setNS "metaeffekt") <$> v .:? "shortName")
      <*> (fmap (setNS "spdx") <$> v .:? "spdxIdentifier")
      <*> v .:? "openCoDEStatus"
      <*> v .:? "alternativeNames" .!= []
      <*> v .:? "otherIds" .!= []

instance ToJSON MetaeffektLicense

instance LicenseFactC MetaeffektLicense where
  getType _ = "MetaeffektLicense"
  getApplicableLNs l =
    let mainNames = maybeToList (_shortName l) ++ _canonicalName l : maybeToList (_spdxIdentifier l)
     in alternativesFromListOfLNs mainNames `ImpreciseLNs` map LN (_category l : _alternativeNames l <> _otherIds l)
  getImpliedStmts l = case _openCoDEStatus l of
    -- https://wikijs.opencode.de/de/Hilfestellungen_und_Richtlinien/Lizenzcompliance
    Just "approved" ->
      let approvedDescription = "Eine Lizenz ist freigegeben, wenn sie nach fachlicher und juristischer Prüfung seitens Open CoDE sowohl der Open Source Definition (gemäß Definition der Open Source Initiative [extern]) entspricht und darüber hinaus keine für die Öffentliche Verwaltung erkennbaren Schwierigkeiten birgt. Außer in Ausnahmefällen ist nicht zu erwarten, dass einmal freigegebene Lizenzen deklassifiziert werden."
       in [LicenseRating (PositiveLicenseRating (ScopedLicenseTag "CoDEStatus" "Approved" (LicenseTagDescription approvedDescription)))]
    Just status -> [LicenseRating (NeutralLicenseRating (ScopedLicenseTag "CoDEStatus" (fromString status) NoLicenseTagText))]
    _ -> []

getMetaeffektLicense :: FilePath -> IO [MetaeffektLicense]
getMetaeffektLicense yaml = do
  logFileReadIO yaml
  decoded <- Y.decodeFileEither yaml :: IO (Either Y.ParseException MetaeffektLicense)
  case decoded of
    Left err -> do
      stderrLogIO ("ERROR: " ++ show err)
      return []
    Right d -> return [d]

data Metaeffekt = Metaeffekt Bool FilePath

instance HasOriginalData Metaeffekt where
  getOriginalData (Metaeffekt _ dir) =
    FromUrl "https://metaeffekt.com/#universe" $
      FromUrl "https://github.com/org-metaeffekt/metaeffekt-universe" $
        FromFile dir NoPreservedOriginalData

instance Source Metaeffekt where
  getSource _ = Source "Metaeffekt"
  getSourceDescription _ = Just "Project providing insights on the {metæffekt} license database."
  getFacts (Metaeffekt dropVariants dir) = do
    yamls <- glob (dir </> "**/*.yaml")
    V.fromList . map wrapFact . filter (\l -> not (dropVariants && isLicenseVariant l)) . mconcat <$> mapM getMetaeffektLicense yamls
