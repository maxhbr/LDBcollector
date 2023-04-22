{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE LambdaCase        #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell   #-}
module Ldbcollector.Source.OSLC
  ( OSLC(..)
  ) where

import           Ldbcollector.Model    hiding (ByteString)

import           Data.ByteString       (ByteString)
import qualified Data.ByteString       as B
import qualified Data.ByteString.Char8 as Char8
import qualified Data.Text             as T
import qualified Data.Vector           as V
import           Data.Yaml

data OSLCUseCase
  = UB
  | MB
  | US
  | MS
  deriving (Show, Eq, Ord, Generic)
instance ToJSON OSLCUseCase
instance FromJSON OSLCUseCase

data OSLCTerm
  = OSLCTerm
  { _termType            :: Text
  , _termDescription     :: Text
  , _termUseCases        :: Maybe [OSLCUseCase]
  , _termComplianceNotes :: Maybe Text
  , _termSeeAlso         :: Maybe [Text]
  } deriving (Show, Eq, Ord, Generic)
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
  { _id        :: Maybe LicenseName
  , _name      :: LicenseName
  , _licenseId :: [LicenseName]
  , _notes     :: Maybe Text
  , _terms     :: Maybe [OSLCTerm]
  } deriving (Show, Eq, Ord, Generic)
instance ToJSON OSLCData
instance FromJSON OSLCData where
  parseJSON = withObject "OSLCData" $ \v -> OSLCData
    <$> pure Nothing
    <*> v .: "name"
    <*> (map (newNLN "spdx") <$> ((v .: "licenseId") <|> fmap (:[]) (v .: "licenseId")))
    <*> v .:? "notes"
    <*> v .:? "terms"

instance LicenseFactC OSLCData where
    getType _ = "OSLC"
    getApplicableLNs (OSLCData {_id = id, _name = name, _licenseId = licenseId}) =
        case maybeToList id ++ [name] ++ licenseId of
            best:others -> LN best `AlternativeLNs` map LN others
            _           -> undefined
    getImpliedStmts oslc =
        [ (MaybeStatement . fmap LicenseComment) (_notes oslc)
        ]

parseYaml :: FilePath -> IO [OSLCData]
parseYaml yaml = do
    logFileReadIO yaml
    let fromFilename = takeBaseName (takeBaseName yaml)
    contents <- readFile yaml
    case decodeEither' (fromString contents) :: Either ParseException [OSLCData] of
        Right decodeds -> return $ map (\decoded -> decoded {_id = (Just . newNLN "oslc" . pack) fromFilename}) decodeds
        Left err -> do
            debugLogIO (show err)
            return mempty

newtype OSLC = OSLC FilePath

instance HasOriginalData OSLC where
    getOriginalData (OSLC dir) = 
        FromUrl "https://github.com/finos/OSLC-handbook" $
        FromFile dir NoPreservedOriginalData
instance Source OSLC where
    getSource _  = Source "OSLC"
    getSourceDescription _ = Just "This handbook provides information on how to comply with some of the more common open source licenses under a specific set of use-cases."
    getFacts (OSLC dir) = do
        yamls <- glob (dir </> "*.yaml")
        V.fromList . map wrapFact . mconcat <$> mapM parseYaml yamls
