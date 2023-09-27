{-# LANGUAGE DeriveAnyClass #-}
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}

module Ldbcollector.Source.Ifross
  ( Ifross (..),
  )
where

import Data.Map qualified as Map
import Data.Text qualified as T
import Data.Vector qualified as V
import Data.Yaml qualified as Y
import Ldbcollector.Model hiding (ByteString)

scope :: String
scope = "ifrOSS"

data IfrossClassification = IfrossClassification
  { _name :: Text,
    _description :: Text,
    _licenses :: Maybe (Map String String),
    _subcategories :: Maybe [IfrossClassification]
  }
  deriving (Show)

$(deriveJSON defaultOptions {fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''IfrossClassification)

data IfrossLicense = IfrossLicense
  { ifrossLicenseName :: LicenseName,
    ifrossLicenseNameShortened :: LicenseName,
    ifrossLicenseUrl :: String,
    ifrossCategoriesWithDescription :: [(Text, Text)]
  }
  deriving (Show, Ord, Eq, Generic, ToJSON)

classificationToLicenses :: [(Text, Text)] -> IfrossClassification -> [IfrossLicense]
classificationToLicenses prefix (IfrossClassification name description licenses subcategories) =
  let cwds = prefix ++ [(name, description)]
      kvToLicense (key, value) =
        IfrossLicense
          (newNLN (T.pack scope) $ pack key)
          ((newLN . T.strip . T.dropWhileEnd (== '(') . pack) key)
          value
          cwds
      fromLicenses = (map kvToLicense . Map.assocs . fromMaybe mempty) licenses
      fromSubcategories = (concatMap (classificationToLicenses cwds) . fromMaybe mempty) subcategories
   in fromLicenses ++ fromSubcategories

categoryWithDescriptionToStmt :: (Text, Text) -> LicenseStatement
categoryWithDescriptionToStmt (classification, description) =
    let positiveRating = LicenseRating $ PositiveLicenseRating (scope ++ " Classification") classification (LicenseRatingDescription description)
        neutralRating  = LicenseRating $ NeutralLicenseRating (scope ++ " Classification") classification (LicenseRatingDescription description)
        negativeRating = LicenseRating $ NegativeLicenseRating (scope ++ " Classification") classification (LicenseRatingDescription description)
     in case classification of
            "Lizenzen ohne Copyleft-Effekt (\"Permissive Licenses\")" -> neutralRating `SubStatements` [LicenseType Permissive]
            "Lizenzen mit strengem Copyleft-Effekt" -> neutralRating `SubStatements` [LicenseType StronglyProtective]
            "Lizenzen mit beschränktem Copyleft-Effekt" -> neutralRating `SubStatements` [LicenseType WeaklyProtective]
            "Lizenzen mit Wahlmöglichkeiten" -> neutralRating `SubStatements` [LicenseType WeaklyProtective]
            "Public Domain Erklärungen" -> negativeRating `SubStatements` [LicenseType PublicDomain]
            "Open Source Lizenzen" -> positiveRating
            "Ethical Licenses" -> negativeRating
            "Sonstige (non-free) Software Lizenzen" -> negativeRating
            _ -> neutralRating

categoriesWithDescriptionToStmt :: [(Text, Text)] -> LicenseStatement
categoriesWithDescriptionToStmt [] = noStmt
categoriesWithDescriptionToStmt [tpl] = categoryWithDescriptionToStmt tpl
categoriesWithDescriptionToStmt (tpl : tpls) = categoryWithDescriptionToStmt tpl `SubStatements` [categoriesWithDescriptionToStmt tpls]

instance LicenseFactC IfrossLicense where
  getType _ = scope ++ " License"
  getApplicableLNs (IfrossLicense ln lnshortened _ _) =
    if ln /= lnshortened
      then LN ln `ImpreciseLNs` [LN lnshortened]
      else LN ln
  getImpliedStmts (IfrossLicense _ _ url tpls) =
    [ LicenseUrl Nothing url,
      categoriesWithDescriptionToStmt (reverse tpls)
    ]

newtype Ifross = Ifross FilePath

instance HasOriginalData Ifross where
  getOriginalData (Ifross yaml) =
    FromUrl "https://ifross.github.io/ifrOSS/Lizenzcenter" $
      FromUrl "https://github.com/ifrOSS/ifrOSS" $
        FromFile yaml NoPreservedOriginalData

instance Source Ifross where
  getSource _ = Source scope
  getFacts (Ifross yaml) = do
    logFileReadIO yaml
    (Y.decodeFileEither yaml :: IO (Either Y.ParseException [IfrossClassification]))
      >>= \case
        Right result -> do
          return ((V.fromList . map wrapFact . concatMap (classificationToLicenses [])) result)
        Left err -> do
          stderrLogIO (show err)
          fail (show err)
