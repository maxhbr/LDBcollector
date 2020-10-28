{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.OSLC
  ( loadOslcFacts
  , oslcLFC
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id, ByteString)
import           Collectors.Common

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8
import           Data.Yaml
import           Data.FileEmbed (embedDir)

import           Model.License

data OSLCUseCase
  = UB
  | MB
  | US
  | MS
  deriving (Show, Generic)
instance ToJSON OSLCUseCase
instance FromJSON OSLCUseCase

data OSLCTerm
  = OSLCTerm
  { termType :: Text
  , termDescription :: Text
  , termUseCases :: Maybe [OSLCUseCase]
  , termComplianceNotes :: Maybe Text
  , termSeeAlso :: Maybe [Text]
  } deriving (Show, Generic)
instance ToJSON OSLCTerm
instance FromJSON OSLCTerm where
  parseJSON = withObject "OSLCTerm" $ \v -> OSLCTerm
    <$> v .: "type"
    <*> v .: "description"
    <*> v .:? "use_cases"
    <*> v .:? "compliance_notes"
    <*> v .:? "seeAlso"

data OSLCData
  = OSLCData
  { name :: LicenseName
  , nameFromFilename :: LicenseName
  , licenseId :: [LicenseName]
  , notes :: Maybe Text
  , terms :: Maybe [OSLCTerm]
  } deriving (Show, Generic)
instance ToJSON OSLCData
instance FromJSON OSLCData where
  parseJSON = withObject "OSLCData" $ \v -> OSLCData
    <$> v .: "name"
    <*> pure ""
    <*> ((v .: "licenseId") <|> fmap (:[]) (v .: "licenseId"))
    <*> v .:? "notes"
    <*> v .:? "terms"
oslcLFC :: LicenseFactClassifier
oslcLFC = LFC "finos-osr/OSLC-handbook"
instance LicenseFactClassifiable OSLCData where
  getLicenseFactClassifier _ = oslcLFC
instance LFRaw OSLCData where
  getImpliedNames (OSLCData _ _ ids _ _) = CLSR ids

loadOslcFactFromFile :: (FilePath, ByteString) -> IO (Vector LicenseFact)
loadOslcFactFromFile (oslcFile, content) = let
    decoded = decodeEither' content :: Either ParseException [OSLCData]
    convertOslcFromFile oslcdFromFile = let
        spdxIds = licenseId oslcdFromFile
        idFromName = if length spdxIds == 1
                     then [name oslcdFromFile]
                     else []
      in map (\i -> LicenseFact
               (Just $ "https://github.com/finos-osr/OSLC-handbook/blob/master/src/" ++ oslcFile)
               oslcdFromFile{ nameFromFilename = dropExtension oslcFile, licenseId = i : idFromName })
             spdxIds
  in case decoded of
       Left pe -> do
         hPutStrLn stderr ("tried to parse " ++ oslcFile ++ ":" ++ show pe)
         return V.empty
       Right oslcdFromBS -> do
         let facts = V.fromList $ concatMap convertOslcFromFile oslcdFromBS
         mapM_ (logThatFileContainedFact oslcFile) facts
         return facts

oslcFolder :: [(FilePath, ByteString)]
oslcFolder = $(embedDir "data/OSLC-handbook/")

loadOslcFacts :: IO Facts
loadOslcFacts = do
  logThatFactsAreLoadedFrom "OSLC-handbook"
  facts <- mapM loadOslcFactFromFile (filter (\(fp,_) -> "yaml" `isSuffixOf` fp) oslcFolder)
  return (V.concat facts)
