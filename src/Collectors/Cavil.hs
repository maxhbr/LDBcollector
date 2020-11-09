{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.Cavil
    ( loadCavilFacts
    , cavilLFC
    ) where

import qualified Prelude as P
import           MyPrelude hiding (ByteString)
import           Collectors.Common

import qualified Data.List as L
import qualified Data.Map as M
import qualified Data.Maybe as M
import           Data.Char (ord)
import qualified Data.Vector as V
import qualified Data.Aeson as A
import           Data.Csv hiding ((.=), (.:))
import qualified Data.Csv as C
import qualified Data.ByteString.Lazy as BL
import           Data.ByteString (ByteString)
import           Collectors.CavilData

import           Model.License

import           Debug.Trace

data CavilJSON =
  CavilJSON
  { license :: LicenseName
  , opinion :: Int
  -- , packname :: String
  , patent :: Int
  -- , pattern :: String
  , risk :: Int
  , trademark :: Int
  -- , unique_id :: String
  } deriving Show
instance FromJSON CavilJSON where
  parseJSON = withObject "CavilJSON" $ \v -> CavilJSON
    <$> v .: "license"
    <*> v .: "opinion"
    <*> v .: "patent"
    <*> v .: "risk"
    <*> v .: "trademark"
mergeCavilJSONs :: [CavilJSON] -> CavilJSON
mergeCavilJSONs ((CavilJSON ln1 o1 p1 r1 t1):jsns) = let
    (CavilJSON _ o2 p2 r2 t2) = mergeCavilJSONs jsns
  in CavilJSON ln1 (max o1 o2) (max p1 p2) (min r1 r2) (max t1 t2)
mergeCavilJSONs [] = CavilJSON "" 0 0 5 0

data CavilCollector =
  CavilCollector [CavilJSON] [LicenseName]
  deriving Show

type CavilCollection = Map LicenseName CavilCollector

addLicenseMapping :: (LicenseName, LicenseName) -> CavilCollection -> CavilCollection
addLicenseMapping (ln,target) col = let
    val = case ln `M.lookup` col of
      Just (CavilCollector jsns ons) -> CavilCollector jsns (target : ons)
      Nothing                        -> CavilCollector [] [target]
  in M.insert ln val col

addLicenseJSON :: CavilJSON -> CavilCollection -> CavilCollection
addLicenseJSON jsn@CavilJSON {license = ln} col = let
    val = case ln `M.lookup` col of
      Just (CavilCollector jsns ons) -> CavilCollector (jsn: jsns) ons
      Nothing                        -> CavilCollector [jsn] []
  in M.insert ln val col

addLicenseJSONs :: [CavilJSON] -> CavilCollection -> CavilCollection
addLicenseJSONs jsns map = L.foldl' (flip addLicenseJSON) map jsns

cavilLFC :: LicenseFactClassifier
cavilLFC = let
    cavilLFL :: LicenseFactLicense
    cavilLFL = LFLWithURL "https://github.com/openSUSE/cavil/blob/master/COPYING" "GPL-2.0"
  in LFCWithURLAndLicense "https://github.com/openSUSE/cavil/tree/master/lib/Cavil/resources" cavilLFL "Cavil"

cavilFolderMap :: Map FilePath ByteString
cavilFolderMap = M.fromList cavilFolder
jsonFiles :: [CavilJSON]
jsonFiles = (M.catMaybes . map A.decode . map (BL.fromStrict . P.snd) . filter (\(fn, _) -> '/' `L.elem` fn)) cavilFolder

parseLicenseChanges :: Either String (Vector (LicenseName, LicenseName))
parseLicenseChanges = case "license_changes.txt" `M.lookup` cavilFolderMap of
  Just strictBS -> C.decodeWith (C.defaultDecodeOptions {decDelimiter = fromIntegral $ ord '\t' }) C.HasHeader (BL.fromStrict strictBS)
  Nothing       -> Left "not found in Map"

data CavilFactRaw
  = CavilFactRaw
  { shortname :: LicenseName
  , otherNames :: [LicenseName]
  , patentInt :: Int
  , riskInt :: Int
  , trademarkInt :: Int
  , opinionInt :: Int
  } deriving (Show, Generic)
instance ToJSON CavilFactRaw
instance LicenseFactClassifiable CavilFactRaw where
  getLicenseFactClassifier _ = cavilLFC
instance LFRaw CavilFactRaw where
  getImpliedNames CavilFactRaw {shortname = sn, otherNames = ons} = CLSR (sn: ons)
  getImpliedId cn@CavilFactRaw {shortname = sn}                   = mkRLSR cn 40 sn

fromCavilCollector :: (LicenseName, CavilCollector) -> CavilFactRaw
fromCavilCollector (ln, CavilCollector jsns ons) = let
    jsn = mergeCavilJSONs jsns
  in CavilFactRaw ln ons (patent jsn) (risk jsn) (trademark jsn) (opinion jsn)

loadCavilFacts :: IO Facts
loadCavilFacts = logThatFactsWithNumberAreLoadedFrom "Cavil" $
  do
    let initialMap = M.empty
    mapFromChanges <- case parseLicenseChanges of
          Left err   -> do
            hPutStrLn stderr $ "err in parseLicenseChanges: " ++ err
            return initialMap
          Right vs -> return $ V.foldl' (flip addLicenseMapping) initialMap vs
    let mapFromJsons = addLicenseJSONs jsonFiles mapFromChanges

    let raws = map fromCavilCollector (M.toAscList mapFromJsons)
        facts = map (LicenseFact Nothing) raws

    return . V.fromList $ facts
