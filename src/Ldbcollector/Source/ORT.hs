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
  { _name :: String
  , _description :: Maybe Text
  } deriving (Show, Eq, Ord, Generic)

$(deriveJSON defaultOptions {fieldLabelModifier = drop 1, constructorTagModifier = map toLower} ''OrtCategory)

data OrtLicenseCategorizationRaw
  = OrtLicenseCategorizationRaw
  { _id :: Text
  , _categories :: [String]
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
  getImpliedStmts (OrtLicenseCategorization _ cs) = 
    map (\(OrtCategory name mdesc) -> case mdesc of
                    Just desc -> stmtWithText name desc
                    _ -> stmt name) cs


factsFromClassificationFile :: OrtLicenseClassificationFile -> [OrtLicenseCategorization]
factsFromClassificationFile (OrtLicenseClassificationFile categories categorizations) = let
        categoriesMap :: Map.Map String OrtCategory
        categoriesMap = (Map.fromList . map (\c -> (_name c,c))) categories
        lookupCategory :: String -> OrtCategory
        lookupCategory key = Map.findWithDefault (OrtCategory key Nothing) key categoriesMap
    in map (\(OrtLicenseCategorizationRaw licenseNameString categories) ->
                OrtLicenseCategorization (newNLN "SPDX" licenseNameString) (map lookupCategory categories)) categorizations


newtype OrtLicenseClassifications
  = OrtLicenseClassifications FilePath

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
        


-- readTxt :: FilePath -> IO (Maybe CALData)
-- readTxt txt = do
--   logFileReadIO txt
--   let fromFilename = takeBaseName (takeBaseName txt)
--   contents <- readFile txt
--   let contentLines = lines contents
--   let parts = (map unlines . Split.splitOn ["---"]) contentLines

--   case parts of
--     _ : yaml : others -> do
--       case Y.decodeEither' ((fromString . ("---\n" ++)) yaml) of
--         Left err -> do
--           debugLogIO (show err)
--           return Nothing
--         Right calData -> return (Just calData {_id = Just ((newNLN "cal" . pack) fromFilename)})
--     _ -> return Nothing -- (return . Add . LicenseName . fromString) fromFilename

instance HasOriginalData OrtLicenseClassifications where
  getOriginalData (OrtLicenseClassifications yaml) =
    FromFile yaml NoPreservedOriginalData

instance Source OrtLicenseClassifications where
  getSource _ = Source "ORT License Classification"
  getFacts (OrtLicenseClassifications yaml) = do
    f <- readClassificationYaml yaml
    (return . V.fromList . map wrapFact . factsFromClassificationFile) f
