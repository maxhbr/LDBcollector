{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.OpenChainPolicyTemplate
  ( loadOCPTFacts
  , ocptLFC
  , loadOCPTFactsFromString -- for testing
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id)
import           Collectors.Common

import qualified Data.Vector as V
import           Debug.Trace (trace)
import qualified Data.ByteString.Lazy as B
import           Data.Csv as C

import           Model.License

data OCPTRow
  = OCPTRow
  { name           :: !String
  , spdxId         :: !String
  , licenseType    :: !String
  , typeCopyleft   :: !String
  , isSaaSDeemed   :: !String
  , freedomOrDeath :: !String
  , commercialUse  :: !Bool
  } deriving (Show, Generic)
-- Name,SPDX Identifier,Type,Copyleft,SaaS Deemed Distribution,Explicit Patent,Freedom or Death,Notice Requirements,Modification Requirements,Commercial Use,Provide Copy of licence ,Same licence,State Changes ,Provide Disclaimer
instance FromField Bool where
  parseField "yes" = pure True
  parseField "no"  = pure False
  parseField _     = pure False
instance FromNamedRecord OCPTRow where
    parseNamedRecord r = OCPTRow <$> r C..: "Name"
                                 <*> r C..: "SPDX Identifier"
                                 <*> r C..: "Type"
                                 <*> r C..: "Copyleft"
                                 <*> r C..: "SaaS Deemed Distribution"
                                 <*> r C..: "Freedom or Death"
                                 <*> r C..: "Commercial Use"
instance ToJSON OCPTRow
ocptLFC :: LicenseFactClassifier
ocptLFC = LFC "OpenChainPolicyTemplate"
instance LFRaw OCPTRow where
  getLicenseFactClassifier _          = ocptLFC
  getImpliedNames OCPTRow{spdxId = i} = CLSR [i]


loadOCPTFactsFromString :: ByteString -> Facts
loadOCPTFactsFromString s = case (decodeByName s :: Either String (Header, V.Vector OCPTRow)) of
  Right (_, v) -> V.map (LicenseFact (Just "https://github.com/OpenChain-Project/curriculum/raw/ddf1e879341adbd9b297cd67c5d5c16b2076540b/policy-template/Open%20Source%20Policy%20Template%20for%20OpenChain%20Specification%201.2.ods")) v
  Left err     -> trace err V.empty

loadOCPTFacts :: FilePath -> IO Facts
loadOCPTFacts osptFile = do
  logThatFactsAreLoadedFrom "Open Chain Policy Template"
  s <- B.readFile osptFile
  return (loadOCPTFactsFromString s)
