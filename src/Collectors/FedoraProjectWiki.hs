{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.FedoraProjectWiki
  ( loadFedoraFacts
  ) where

import Prelude hiding (id)

import           System.FilePath
import qualified Data.Text as T
import qualified Data.Vector as V
import           Debug.Trace (trace)
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)
import           Control.Applicative
import           Data.Csv as C
import           Data.Aeson as A
import           GHC.Generics

import           Model.License
import           Model.Utils


data FedoraProjectWikiFact_Core
  = FedoraProjectWikiFact_Core LicenseName
                               (Maybe String)
                               (Maybe String)
  deriving (Show, Generic)
instance FromNamedRecord FedoraProjectWikiFact_Core where
    parseNamedRecord r = FedoraProjectWikiFact_Core <$> r C..: "Full Name"
                                                    <*> r C..: "FSF Free?"
                                                    <*> r C..: "Upstream URL"
instance ToJSON FedoraProjectWikiFact_Core
instance LFRaw FedoraProjectWikiFact_Core where
  getImpliedNames (FedoraProjectWikiFact_Core fn _ _) = [fn] -- the shortnames are not good here
  getType _                                           = "FPWFact"

-- Full Name,FSF Free?,Upstream URL,Notes
data FedoraProjectWikiFact_Bad
  = FedoraProjectWikiFact_Bad FedoraProjectWikiFact_Core
                              (Maybe String)
  deriving (Show, Generic)
instance ToJSON FedoraProjectWikiFact_Bad
instance FromNamedRecord FedoraProjectWikiFact_Bad where
    parseNamedRecord r = FedoraProjectWikiFact_Bad <$> (parseNamedRecord r :: C.Parser FedoraProjectWikiFact_Core)
                                                   <*> r C..: "Notes"
instance LFRaw FedoraProjectWikiFact_Bad where
  getImpliedNames (FedoraProjectWikiFact_Bad c _) = getImpliedNames c
  getType (FedoraProjectWikiFact_Bad c _)         = getType c


-- Full Name,Short Name,FSF Free?,Upstream URL
data FedoraProjectWikiFact_Short
  = FedoraProjectWikiFact_Short FedoraProjectWikiFact_Core
                                (Maybe LicenseName)
  deriving (Show, Generic)
instance ToJSON FedoraProjectWikiFact_Short
instance FromNamedRecord FedoraProjectWikiFact_Short where
    parseNamedRecord r = FedoraProjectWikiFact_Short <$> (parseNamedRecord r :: C.Parser FedoraProjectWikiFact_Core)
                                                     <*> r C..: "Short Name"
instance LFRaw FedoraProjectWikiFact_Short where
  getImpliedNames (FedoraProjectWikiFact_Short c _) = getImpliedNames c
  getType (FedoraProjectWikiFact_Short c _)         = getType c

-- Full Name,Short Name,FSF Free?,GPLv2 Compat?,GPLv3 Compat?,Upstream URL
data FedoraProjectWikiFact_Full
  = FedoraProjectWikiFact_Full FedoraProjectWikiFact_Short
                               (Maybe String)
                               (Maybe String)
  deriving (Show, Generic)
instance ToJSON FedoraProjectWikiFact_Full
instance FromNamedRecord FedoraProjectWikiFact_Full where
    parseNamedRecord r = FedoraProjectWikiFact_Full <$> (parseNamedRecord r :: C.Parser FedoraProjectWikiFact_Short)
                                               <*> r C..: "GPLv2 Compat?"
                                               <*> r C..: "GPLv3 Compat?"
instance LFRaw FedoraProjectWikiFact_Full where
  getImpliedNames (FedoraProjectWikiFact_Full s _ _) = getImpliedNames s
  getType (FedoraProjectWikiFact_Full s _ _)         = getType s

data FedoraProjectWikiFact
  = FedoraProjectWikiFact String
                          (Either (Either FedoraProjectWikiFact_Full FedoraProjectWikiFact_Short) FedoraProjectWikiFact_Bad)
  deriving (Show, Generic)
instance ToJSON FedoraProjectWikiFact where
  toJSON (FedoraProjectWikiFact t d) = let
      aesonFromCore :: FedoraProjectWikiFact_Core -> Value
      aesonFromCore (FedoraProjectWikiFact_Core n fsf url) = object [ "Full Name" A..= n
                                                                    , "FSF Free?" A..= fsf
                                                                    , "Upstream URL" A..= url ]
      aesonFromDataShort :: FedoraProjectWikiFact_Short -> Value
      aesonFromDataShort (FedoraProjectWikiFact_Short c sn) = mergeAesonL [ aesonFromCore c
                                                                          , object ["Shot Name" A..= sn] ]
      aesonFromDataBad :: FedoraProjectWikiFact_Bad -> Value
      aesonFromDataBad (FedoraProjectWikiFact_Bad c ns) = mergeAesonL [ aesonFromCore c
                                                                      , object ["Notes" A..= ns] ]
      aesonFromDataFull :: FedoraProjectWikiFact_Full -> Value
      aesonFromDataFull (FedoraProjectWikiFact_Full short gl2 gl3) = mergeAesonL [ aesonFromDataShort short
                                                                                 , object [ "GPLv2 Compat?" A..= gl2
                                                                                          , "GPLv3 Compat?" A..= gl3 ] ]
      aesonFromData :: Value
      aesonFromData = case d of
                        (Left (Left full))   -> aesonFromDataFull full
                        (Left (Right short)) -> aesonFromDataShort short
                        (Right bad)          -> aesonFromDataBad bad
      rankingFromData :: String
      rankingFromData = case d of
        (Left _)  -> "Good"
        (Right _) -> "Bad"
    in mergeAesonL [ object [ "licenseType" A..= t
                            , "rating" A..= rankingFromData ]
                   , aesonFromData ]
  -- toJSON (FedoraProjectWikiFact t (Left (Right short))) = undefined
  -- toJSON (FedoraProjectWikiFact t (Right bad)) = undefined
instance LFRaw FedoraProjectWikiFact where
  getImpliedNames (FedoraProjectWikiFact _ (Left (Left full)))   = getImpliedNames full
  getImpliedNames (FedoraProjectWikiFact _ (Left (Right short))) = getImpliedNames short
  getImpliedNames (FedoraProjectWikiFact _ (Right bad))          = getImpliedNames bad
  getType _                                                      = "FPWFact"

toFPWF_Full :: String -> FedoraProjectWikiFact_Full -> FedoraProjectWikiFact
toFPWF_Full t full = FedoraProjectWikiFact t (Left (Left full))
toFPWF_Short :: String -> FedoraProjectWikiFact_Short -> FedoraProjectWikiFact
toFPWF_Short t short =  FedoraProjectWikiFact t (Left (Right short))
toFPWF_Bad :: String -> FedoraProjectWikiFact_Bad -> FedoraProjectWikiFact
toFPWF_Bad t bad =  FedoraProjectWikiFact t (Right bad)

-- TODO: replace Good/Baad by data
-- TODO: replace type by data
loadFedoraFactsFromByteString :: String -> String -> ByteString -> Facts
loadFedoraFactsFromByteString t "Good" s = case (decodeByName s :: Either String (Header, V.Vector FedoraProjectWikiFact_Full)) of
                                             Right (_, v) -> V.map (mkLicenseFact "FedoraProjectWiki" . toFPWF_Full t) v
                                             Left err1    ->  case (decodeByName s :: Either String (Header, V.Vector FedoraProjectWikiFact_Short)) of
                                                                Right (_, v) -> V.map (mkLicenseFact "FedoraProjectWiki" . toFPWF_Short t) v
                                                                Left err2    -> trace (err1 ++ err2) V.empty
loadFedoraFactsFromByteString t "Bad" s = case (decodeByName s :: Either String (Header, V.Vector FedoraProjectWikiFact_Bad)) of
                                            Right (_, v) -> V.map (mkLicenseFact "FedoraProjectWiki" . toFPWF_Bad t) v
                                            Left err     -> trace (err) V.empty
loadFedoraFactsFromByteString _ _ _ = undefined


loadFedoraFactsFromFile :: String -> String -> FilePath -> IO Facts
loadFedoraFactsFromFile t r csv = do
  s <- B.readFile csv
  return (loadFedoraFactsFromByteString t r s)

loadFedoraFacts :: FilePath -> IO Facts
loadFedoraFacts fedoraFactsDir = do
  lgfs <- loadFedoraFactsFromFile "license" "Good" (fedoraFactsDir </> "Fedora_Project_Wiki-Good_Licenses.csv")
  lbfs <- loadFedoraFactsFromFile "license" "Bad" (fedoraFactsDir </> "Fedora_Project_Wiki-Bad_Licenses.csv")
  lfgfs <- loadFedoraFactsFromFile "font license" "Good" (fedoraFactsDir </> "Fedora_Project_Wiki-Good_Font_Licenses.csv")
  lfbfs <- loadFedoraFactsFromFile "font license" "Bad" (fedoraFactsDir </> "Fedora_Project_Wiki-Bad_Font_Licenses.csv")
  lcgfs <- loadFedoraFactsFromFile "content license" "Good" (fedoraFactsDir </> "Fedora_Project_Wiki-Good_Content_Licenses.csv")
  lcbfs <- loadFedoraFactsFromFile "content license" "Bad" (fedoraFactsDir </> "Fedora_Project_Wiki-Bad_Content_Licenses.csv")
  ldgfs <- loadFedoraFactsFromFile "documentation license" "Good" (fedoraFactsDir </> "Fedora_Project_Wiki-Good_Documentation_Licenses.csv")
  ldbfs <- loadFedoraFactsFromFile "documentation license" "Bad" (fedoraFactsDir </> "Fedora_Project_Wiki-Bad_Documentation_Licenses.csv")
  return $ V.concat [ lgfs
                    , lbfs
                    , lfgfs
                    , lfbfs
                    , lcgfs
                    , lcbfs
                    , ldgfs
                    , ldbfs ]
