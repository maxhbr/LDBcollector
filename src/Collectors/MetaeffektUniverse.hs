{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell   #-}
{-# LANGUAGE TupleSections     #-}

module Collectors.MetaeffektUniverse
  ( loadMetaeffektUniverseFacts
  , metaeffektUniverseLFC
  ) where

import           Collectors.Common
import           MyPrelude             hiding (ByteString, id)
import qualified Prelude               as P

import           Data.ByteString       (ByteString)
import qualified Data.ByteString       as B
import qualified Data.ByteString.Char8 as Char8
import           Data.FileEmbed        (embedDir)
import qualified Data.Map              as Map
import qualified Data.Maybe            as Maybe
import           Data.Text.Encoding    (decodeUtf8)
import qualified Data.Vector           as V
import           Data.Yaml

import           Model.License

import           Debug.Trace

metaeffektUniverseFolder :: [(FilePath, ByteString)]
metaeffektUniverseFolder = $(embedDir "data/metaeffekt-universe/")

loadMetaeffektUniverseFacts :: IO Facts
loadMetaeffektUniverseFacts =
  let scancodeLicenseFolderMap = Map.fromList metaeffektUniverseFolder
      ymls =
        filter (\(k, v) -> "yaml" `isSuffixOf` k) $ metaeffektUniverseFolder
      facts =
        foldl (V.++) V.empty $ map loadMetaeffektUniverseFactsFromData ymls
   in do logThatFactsAreLoadedFrom "Metaeffekt Universe"
         return facts

loadMetaeffektUniverseFactsFromData :: (FilePath, ByteString) -> Facts
loadMetaeffektUniverseFactsFromData (fn, yml) =
  let decoded =
        decodeEither' yml :: (Either ParseException MetaeffektUniverseData)
   in case decoded of
        Left pe -> trace (show pe) V.empty
        Right medFromRow ->
          V.singleton
            (LicenseFact
               (Just $
                "https://github.com/org-metaeffekt/metaeffekt-universe/blob/main/" ++
                fn)
               medFromRow)

data MetaeffektUniverseData =
  MetaeffektUniverseData
    { canonicalName    :: !String
    , category         :: Maybe String
    , shortName        :: Maybe String
    , spdxIdentifier   :: Maybe String
    , alternativeNames :: [String]
    , otherIds         :: [String]
    }
  deriving (Show, Generic)

instance FromJSON MetaeffektUniverseData where
  parseJSON =
    withObject "MetaeffektUniverseData" $ \v ->
      MetaeffektUniverseData <$> v .: "canonicalName" <*> v .:? "category" <*>
      v .:? "shortName" <*>
      v .:? "spdxIdentifier" <*>
      (Maybe.fromMaybe [] <$> v .:? "alternativeNames") <*>
      (Maybe.fromMaybe [] <$> v .:? "otherIds")

instance ToJSON MetaeffektUniverseData

metaeffektUniverseLFC :: LicenseFactClassifier
metaeffektUniverseLFC = LFCWithLicense (LFL "CC-BY-4.0") "Metaeffekt Universe"

instance LicenseFactClassifiable MetaeffektUniverseData where
  getLicenseFactClassifier _ = metaeffektUniverseLFC

instance LFRaw MetaeffektUniverseData where
  getImpliedNames me@MetaeffektUniverseData { canonicalName = cn
                                            , shortName = msn
                                            , spdxIdentifier = msi
                                            , otherIds = ois
                                            } =
    CLSR $ [cn] ++ (Maybe.maybeToList msn) ++ (Maybe.maybeToList msi) ++ ois
  getImpliedAmbiguousNames me@MetaeffektUniverseData {alternativeNames = mans} =
    CLSR $ mans
  getImpliedId me@MetaeffektUniverseData {spdxIdentifier = Just si} =
    mkRLSR me 90 si
  getImpliedId me@MetaeffektUniverseData {shortName = Just sn} = mkRLSR me 80 sn
  getImpliedId me@MetaeffektUniverseData {canonicalName = cn} = mkRLSR me 60 cn
  getImpliedComments me@MetaeffektUniverseData {category = Just c} =
    mkSLSR me ["category: " ++ c]
  getImpliedComments _ = getEmptyLicenseStatement
