{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Ldbcollector.Source.OSLC
  ( OSLC(..)
  ) where

import           Ldbcollector.Model    hiding (ByteString)

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString as B
import           Data.ByteString (ByteString)
import qualified Data.ByteString.Char8 as Char8
import           Data.Yaml

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
  { _termType :: Text
  , _termDescription :: Text
  , _termUseCases :: Maybe [OSLCUseCase]
  , _termComplianceNotes :: Maybe Text
  , _termSeeAlso :: Maybe [Text]
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
  { _name :: LicenseName
  , _licenseId :: [LicenseName]
  , _notes :: Maybe Text
  , _terms :: Maybe [OSLCTerm]
  } deriving (Show, Generic)
instance ToJSON OSLCData
instance FromJSON OSLCData where
  parseJSON = withObject "OSLCData" $ \v -> OSLCData
    <$> v .: "name"
    <*> ((v .: "licenseId") <|> fmap (:[]) (v .: "licenseId"))
    <*> v .:? "notes"
    <*> v .:? "terms"

newtype OSLC = OSLC FilePath

applyDecoded :: String -> OSLCData -> LicenseGraphTask
applyDecoded fromFilename oslc =
    EdgeLeft (AddTs . V.fromList $
        [ maybeToTask (Add . Data) (_notes oslc)
        ]) AppliesTo $
    EdgeLeft ((Add . LicenseName . _name) oslc) (Potentially Better) $
    Edge (fromValue oslc (const $ (LicenseName . newNLN "oslc" . pack) fromFilename) (const Nothing)) Better $
        (Adds . V.fromList . map (LicenseName . setNS "spdx") . _licenseId) oslc

applyYaml :: FilePath -> IO LicenseGraphTask
applyYaml yaml = do
    putStrLn ("read " ++ yaml)
    let fromFilename = takeBaseName (takeBaseName yaml)
    contents <- readFile yaml
    case decodeEither' (fromString contents) :: Either ParseException [OSLCData] of
        Left err -> do
                putStrLn (show err)
                return Noop
        Right decodeds -> (return . AddTs . V.fromList) $ map (applyDecoded fromFilename) decodeds

instance Source OSLC where
    getTask (OSLC dir) = do
        yamls <- glob (dir </> "*.yaml")
        AddTs . V.fromList <$> mapM applyYaml yamls
