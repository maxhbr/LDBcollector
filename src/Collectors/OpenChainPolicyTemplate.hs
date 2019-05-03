{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.OpenChainPolicyTemplate
  ( loadOSPTFacts
  , loadOSPTFactsFromString
  ) where

import qualified Prelude as P
import           MyPrelude hiding (id)

import qualified Data.Vector as V
import           Debug.Trace (trace)
import qualified Data.ByteString.Lazy as B
import           Data.Csv as C

import Data.Aeson
import GHC.Generics

import           Model.License

data OSPTRow
  = OSPTRow
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
instance FromNamedRecord OSPTRow where
    parseNamedRecord r = OSPTRow <$> r C..: "Name"
                                 <*> r C..: "SPDX Identifier"
                                 <*> r C..: "Type"
                                 <*> r C..: "Copyleft"
                                 <*> r C..: "SaaS Deemed Distribution"
                                 <*> r C..: "Freedom or Death"
                                 <*> r C..: "Commercial Use"
instance ToJSON OSPTRow
instance LFRaw OSPTRow where
  getLicenseFactClassifier _          = LFC ["OpenChainPolicyTemplate", "OCPTRow"]
  getImpliedNames OSPTRow{spdxId = i} = [i]


loadOSPTFactsFromString :: ByteString -> Facts
loadOSPTFactsFromString s = case (decodeByName s :: Either String (Header, V.Vector OSPTRow)) of
  Right (_, v) -> V.map LicenseFact v
  Left err     -> trace err V.empty

loadOSPTFacts :: FilePath -> IO Facts
loadOSPTFacts osptFile = do
  s <- B.readFile osptFile
  return (loadOSPTFactsFromString s)
