{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Collectors.FedoraProjectWiki
  ( loadFedoraFacts
  , fedoraLFC
  ) where

import qualified Prelude as P
import           MyPrelude
import           Collectors.Common

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as B
import qualified Data.Map as Map
import           Control.Applicative
import           Data.Csv as C
import           Data.Aeson as A
import           Data.FileEmbed (embedDir)

import           Model.License

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
class HasFedoraProjectWikiFactCore a where
  getFedoraProjectWikiCore :: a -> FedoraProjectWikiFact_Core
  getFullNameFromCore :: a -> LicenseName
  getFullNameFromCore a = case getFedoraProjectWikiCore a of
    (FedoraProjectWikiFact_Core fn _ _) -> fn

-- Full Name,FSF Free?,Upstream URL,Notes
data FedoraProjectWikiFact_Bad
  = FedoraProjectWikiFact_Bad FedoraProjectWikiFact_Core
                              (Maybe String)
  deriving (Show, Generic)
instance ToJSON FedoraProjectWikiFact_Bad
instance FromNamedRecord FedoraProjectWikiFact_Bad where
    parseNamedRecord r = FedoraProjectWikiFact_Bad <$> (parseNamedRecord r :: C.Parser FedoraProjectWikiFact_Core)
                                                   <*> r C..: "Notes"
instance HasFedoraProjectWikiFactCore FedoraProjectWikiFact_Bad where
  getFedoraProjectWikiCore (FedoraProjectWikiFact_Bad c _) = c


-- Full Name,Short Name,FSF Free?,Upstream URL
data FedoraProjectWikiFact_Short
  = FedoraProjectWikiFact_Short FedoraProjectWikiFact_Core
                                (Maybe LicenseName)
  deriving (Show, Generic)
instance ToJSON FedoraProjectWikiFact_Short
instance FromNamedRecord FedoraProjectWikiFact_Short where
    parseNamedRecord r = FedoraProjectWikiFact_Short <$> (parseNamedRecord r :: C.Parser FedoraProjectWikiFact_Core)
                                                     <*> r C..: "Short Name" -- Short names are of bad quality here
instance HasFedoraProjectWikiFactCore FedoraProjectWikiFact_Short where
  getFedoraProjectWikiCore (FedoraProjectWikiFact_Short c _) = c

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
instance HasFedoraProjectWikiFactCore FedoraProjectWikiFact_Full where
  getFedoraProjectWikiCore (FedoraProjectWikiFact_Full s _ _) = getFedoraProjectWikiCore s

data FedoraProjectWikiFact
  = FedoraProjectWikiFact String
                          (Either (Either FedoraProjectWikiFact_Full FedoraProjectWikiFact_Short) FedoraProjectWikiFact_Bad)
  deriving (Show, Generic)
instance HasFedoraProjectWikiFactCore FedoraProjectWikiFact where
  getFedoraProjectWikiCore (FedoraProjectWikiFact _ (Left (Left full)))   = getFedoraProjectWikiCore full
  getFedoraProjectWikiCore (FedoraProjectWikiFact _ (Left (Right short))) = getFedoraProjectWikiCore short
  getFedoraProjectWikiCore (FedoraProjectWikiFact _ (Right bad))          = getFedoraProjectWikiCore bad
instance ToJSON FedoraProjectWikiFact where
  toJSON (FedoraProjectWikiFact t d) = let
      aesonFromCore :: FedoraProjectWikiFact_Core -> Value
      aesonFromCore (FedoraProjectWikiFact_Core n fsf url) = object [ "Full Name" A..= n
                                                                    , "FSF Free?" A..= fsf
                                                                    , "Upstream URL" A..= url ]
      aesonFromDataShort :: FedoraProjectWikiFact_Short -> Value
      aesonFromDataShort (FedoraProjectWikiFact_Short c sn) = mergeAesonL [ aesonFromCore c
                                                                          , object ["Short Name" A..= sn] ]
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
fedoraLFC :: LicenseFactClassifier
fedoraLFC = LFC "Fedora Project Wiki"
instance LicenseFactClassifiable FedoraProjectWikiFact where
  getLicenseFactClassifier _ = fedoraLFC
instance LFRaw FedoraProjectWikiFact where
  getImpliedNames (FedoraProjectWikiFact _ (Left (Left full)))   = CLSR [getFullNameFromCore full]
  getImpliedNames (FedoraProjectWikiFact _ (Left (Right short))) = CLSR [getFullNameFromCore short]
  getImpliedNames (FedoraProjectWikiFact _ (Right bad))          = CLSR [getFullNameFromCore bad]
  getImpliedJudgement fpwf@(FedoraProjectWikiFact _ (Right _))   = SLSR (getLicenseFactClassifier fpwf) $ NegativeJudgement "This software licenses which is NOT OKAY for Fedora. Nothing in Fedora is permitted to use this license. It is either non-free or deprecated."
  getImpliedJudgement fpwf                                       = SLSR (getLicenseFactClassifier fpwf) $ PositiveJudgement "This software Licenses is OK for Fedora"
  getImpliedIsFSFFree fpwf                                       = case getFedoraProjectWikiCore fpwf of
    (FedoraProjectWikiFact_Core _ (Just "Yes") _) -> mkRLSR fpwf 50 True
    (FedoraProjectWikiFact_Core _ (Just "NO") _)  -> mkRLSR fpwf 50 False
    _                                             -> NoRLSR

toFPWF_Full :: String -> FedoraProjectWikiFact_Full -> FedoraProjectWikiFact
toFPWF_Full t full = FedoraProjectWikiFact t (Left (Left full))
toFPWF_Short :: String -> FedoraProjectWikiFact_Short -> FedoraProjectWikiFact
toFPWF_Short t short =  FedoraProjectWikiFact t (Left (Right short))
toFPWF_Bad :: String -> FedoraProjectWikiFact_Bad -> FedoraProjectWikiFact
toFPWF_Bad t bad =  FedoraProjectWikiFact t (Right bad)

toFedoraLicenseFact :: LFRaw a => a -> LicenseFact
toFedoraLicenseFact = LicenseFact (Just "https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing")

-- TODO: replace Good/Baad by data
-- TODO: replace type by data
loadFedoraFactsFromByteString :: String -> String -> ByteString -> Facts
loadFedoraFactsFromByteString t "Good" s = case (decodeByName s :: Either String (Header, V.Vector FedoraProjectWikiFact_Full)) of
                                             Right (_, v) -> V.map (toFedoraLicenseFact . toFPWF_Full t) v
                                             Left err1    ->  case (decodeByName s :: Either String (Header, V.Vector FedoraProjectWikiFact_Short)) of
                                                                Right (_, v) -> V.map (toFedoraLicenseFact . toFPWF_Short t) v
                                                                Left err2    -> trace (err1 ++ err2) V.empty
loadFedoraFactsFromByteString t "Bad" s = case (decodeByName s :: Either String (Header, V.Vector FedoraProjectWikiFact_Bad)) of
                                            Right (_, v) -> V.map (toFedoraLicenseFact . toFPWF_Bad t) v
                                            Left err     -> trace err V.empty
loadFedoraFactsFromByteString _ _ _ = undefined


fpwFolder :: Map.Map FilePath ByteString
fpwFolder = Map.map (B.fromStrict) $ Map.fromList ( $(embedDir "data/Fedora_Project_Wiki/") )

loadFedoraFacts :: IO Facts
loadFedoraFacts = let
    lgfs = loadFedoraFactsFromByteString "license" "Good" (fpwFolder Map.! "Fedora_Project_Wiki-Good_Licenses.csv")
    lbfs = loadFedoraFactsFromByteString "license" "Bad" (fpwFolder Map.! "Fedora_Project_Wiki-Bad_Licenses.csv")
    lfgfs = loadFedoraFactsFromByteString "font license" "Good" (fpwFolder Map.! "Fedora_Project_Wiki-Good_Font_Licenses.csv")
    lfbfs = loadFedoraFactsFromByteString "font license" "Bad" (fpwFolder Map.! "Fedora_Project_Wiki-Bad_Font_Licenses.csv")
    lcgfs = loadFedoraFactsFromByteString "content license" "Good" (fpwFolder Map.! "Fedora_Project_Wiki-Good_Content_Licenses.csv")
    lcbfs = loadFedoraFactsFromByteString "content license" "Bad" (fpwFolder Map.! "Fedora_Project_Wiki-Bad_Content_Licenses.csv")
    ldgfs = loadFedoraFactsFromByteString "documentation license" "Good" (fpwFolder Map.! "Fedora_Project_Wiki-Good_Documentation_Licenses.csv")
    ldbfs = loadFedoraFactsFromByteString "documentation license" "Bad" (fpwFolder Map.! "Fedora_Project_Wiki-Bad_Documentation_Licenses.csv")
  in do
    logThatFactsAreLoadedFrom "Fedora Project Wiki"
    return $ V.concat [ lgfs
                      , lbfs
                      , lfgfs
                      , lfbfs
                      , lcgfs
                      , lcbfs
                      , ldgfs
                      , ldbfs ]
