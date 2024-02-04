{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}

module Ldbcollector.Source.ORT
  ( OrtLicenseClassifications (..),
  )
where

import Data.List.Split qualified as Split
import Data.Vector qualified as V
import Data.Yaml qualified as Y
import Ldbcollector.Model hiding (ByteString)
import Text.Blaze.Html5 qualified as H
import qualified Data.Map as Map


data OrtCategory
  = OrtCategory
  { _name :: Text
  , _description :: Maybe Text
  } deriving (Show, Eq, Ord, Generic)

$(deriveJSON defaultOptions {fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''OrtCategory)

data OrtLicenseCategorizationRaw
  = OrtLicenseCategorizationRaw
  { _id :: Text
  , _categories :: [Text]
  } deriving (Show, Eq, Ord, Generic)

$(deriveJSON defaultOptions {fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''OrtLicenseCategorizationRaw)

data OrtLicenseClassificationFile
  = OrtLicenseClassificationFile
  { __categories :: [OrtCategory]
  , __categorizations :: [OrtLicenseCategorizationRaw]
  } deriving (Show, Eq, Ord, Generic)

$(deriveJSON defaultOptions {fieldLabelModifier = drop 2, constructorTagModifier = map toLower} ''OrtLicenseClassificationFile)

data OrtLicenseCategorization
  = OrtLicenseCategorization
  { _olcLicensename :: LicenseName
  , _olcCategories :: [OrtCategory]
  } deriving (Show, Eq, Ord, Generic)
  
instance ToJSON OrtLicenseCategorization

instance LicenseFactC OrtLicenseCategorization where
  getType _ = "OrtLicenseCategorization"
  getApplicableLNs (OrtLicenseCategorization ln _)  = LN ln
  getImpliedStmts a@(OrtLicenseCategorization _ cs) = 
    map (\(OrtCategory name mdesc) -> case mdesc of
                    Just desc -> scopedTagStmt (getType a) name desc
                    _ -> LicenseTag (ScopedLicenseTag (getType a) name NoLicenseTagText)) cs


factsFromClassificationFile :: OrtLicenseClassificationFile -> [OrtLicenseCategorization]
factsFromClassificationFile (OrtLicenseClassificationFile categories categorizations) = let
        categoriesMap :: Map.Map Text OrtCategory
        categoriesMap = (Map.fromList . map (\c -> (_name c,c))) categories
        lookupCategory :: Text -> OrtCategory
        lookupCategory key = Map.findWithDefault (OrtCategory key Nothing) key categoriesMap
    in map (\(OrtLicenseCategorizationRaw licenseNameString categories) ->
                OrtLicenseCategorization (newNLN "SPDX" licenseNameString) (map lookupCategory categories)) categorizations


data OrtLicenseClassifications
  = OrtLicenseClassifications String FilePath

readClassificationYaml :: FilePath -> IO OrtLicenseClassificationFile
readClassificationYaml yaml = 
    do
      logFileReadIO yaml
      decoded <- Y.decodeFileEither yaml :: IO (Either Y.ParseException OrtLicenseClassificationFile)
      case decoded of
        Left err -> do
          stderrLogIO ("ERROR: " ++ show err)
          undefined -- TODO ;) 
        Right f -> return f

instance HasOriginalData OrtLicenseClassifications where
  getOriginalData (OrtLicenseClassifications _ yaml) =
    FromFile yaml NoPreservedOriginalData

instance Source OrtLicenseClassifications where
  getSource (OrtLicenseClassifications source _) = Source source
  getFacts (OrtLicenseClassifications _ yaml) = do
    f <- readClassificationYaml yaml
    (return . V.fromList . map wrapFact . factsFromClassificationFile) f