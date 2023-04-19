{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE DeriveAnyClass    #-}
{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell   #-}
module Ldbcollector.Source.Ifross
    ( Ifross (..)
    ) where

import           Ldbcollector.Model hiding (ByteString)

import qualified Data.Map           as Map
import qualified Data.Vector        as V
import qualified Data.Yaml          as Y
import qualified Data.Text          as T

data IfrossClassification
    = IfrossClassification
    { _name :: Text
    , _description :: Text
    , _licenses :: Maybe (Map String String)
    , _subcategories :: Maybe [IfrossClassification]
    } deriving (Show)
$(deriveJSON defaultOptions{fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''IfrossClassification)

data IfrossLicense
    = IfrossLicense
    { ifrossLicenseName :: LicenseName
    , ifrossLicenseNameShortened :: LicenseName
    , ifrossLicenseUrl :: String
    , ifrossCategoriesWithDescription :: [(Text,Text)]
    }
    deriving (Show, Ord, Eq, Generic, ToJSON)


classificationToLicenses :: [(Text,Text)] -> IfrossClassification -> [IfrossLicense]
classificationToLicenses prefix (IfrossClassification name description licenses subcategories) = let
        cwds = prefix ++ [(name, description)]
        kvToLicense (key, value) = IfrossLicense (newNLN "ifross" $ pack key) ((newLN . T.strip . T.dropWhileEnd (=='(') . pack) key) value cwds
        fromLicenses = (map kvToLicense . Map.assocs . fromMaybe mempty) licenses
        fromSubcategories = (concatMap (classificationToLicenses cwds) . fromMaybe mempty) subcategories
    in fromLicenses ++ fromSubcategories

addParsedType :: Text -> LicenseStatement -> LicenseStatement
addParsedType "Lizenzen ohne Copyleft-Effekt (\"Permissive Licenses\")" stmt = stmt `SubStatements` [LicenseType Permissive]
addParsedType "Lizenzen mit strengem Copyleft-Effekt" stmt = stmt `SubStatements` [LicenseType StronglyProtective]
addParsedType "Lizenzen mit beschränktem Copyleft-Effekt" stmt = stmt `SubStatements` [LicenseType WeaklyProtective]
addParsedType "Lizenzen mit Wahlmöglichkeiten" stmt = stmt `SubStatements` [LicenseType WeaklyProtective]
addParsedType "Public Domain Erklärungen" stmt = stmt `SubStatements` [LicenseType PublicDomain]
addParsedType n@"Open Source Lizenzen" stmt = stmt `SubStatements` [LicenseRating (PositiveLicenseRating "ifrOSS" n Nothing)]
addParsedType n@"Ethical Licenses" stmt = stmt `SubStatements` [LicenseRating (NegativeLicenseRating "ifrOSS" n Nothing)]
addParsedType n@"Sonstige (non-free) Software Lizenzen" stmt = stmt `SubStatements` [LicenseRating (NegativeLicenseRating "ifrOSS" n Nothing)]
addParsedType _ stmt = stmt
categoryWithDescriptionToStmt :: (Text,Text) -> LicenseStatement
categoryWithDescriptionToStmt (classification,description) =
    addParsedType classification $ LicenseComment classification `SubStatements` [LicenseComment description]
categoriesWithDescriptionToStmt :: [(Text,Text)] -> LicenseStatement
categoriesWithDescriptionToStmt [] = noStmt
categoriesWithDescriptionToStmt [tpl] = categoryWithDescriptionToStmt tpl
categoriesWithDescriptionToStmt (tpl:tpls) = categoryWithDescriptionToStmt tpl `SubStatements` [categoriesWithDescriptionToStmt tpls]

instance LicenseFactC IfrossLicense where
    getType _ = "ifrOSS License"
    getApplicableLNs (IfrossLicense ln lnshortened _ _) = 
        if ln /= lnshortened
            then LN ln `ImpreciseLNs` [LN lnshortened]
            else LN ln
    getImpliedStmts (IfrossLicense _ _ url tpls) = [ LicenseUrl url 
                                                   , categoriesWithDescriptionToStmt (reverse tpls)
                                                   ]

newtype Ifross = Ifross FilePath
instance Source Ifross where
    getSource _  = Source "ifrOSS"
    getFacts (Ifross yaml) = do
        logFileReadIO yaml
        (Y.decodeFileEither yaml :: IO (Either Y.ParseException [IfrossClassification])) >>=
            \case
                Right result -> do
                    return ((V.fromList . map wrapFact . concatMap (classificationToLicenses [])) result)
                Left err -> do
                    stderrLogIO (show err)
                    fail (show err)
