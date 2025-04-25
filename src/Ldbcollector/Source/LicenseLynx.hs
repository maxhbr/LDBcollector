{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Ldbcollector.Source.LicenseLynx where

import Data.Aeson
import Data.Aeson.Types (Object, Parser, withArray, withObject)
import Data.Aeson.KeyMap qualified as KM
import Data.Aeson.Key qualified as K
import Data.ByteString.Lazy (ByteString)
import Data.Text (Text)
import Data.Text.IO qualified as T
import Data.Vector qualified as V
import Ldbcollector.Model


data LicenseLynx = LicenseLynx {
    licenseLynxCanonical :: LicenseName,
    licenseLynxAliases :: [LicenseName],
    licenseLynxSrc :: Text
} deriving (Show, Eq, Generic)

instance ToJSON LicenseLynx where
    toJSON = genericToJSON defaultOptions { fieldLabelModifier = camelTo2 '_' }

parsePair :: (Key, Value) -> Parser [LicenseName]
parsePair ("custom", aliases) = 
    (fmap (map newLN) . parseJSON) aliases
    -- withArray "aliases" $ fmap (map (newNLN "custom")) . mapM parseJSON
parsePair (aliasScope, aliases) = do
    let knownAliasScopes = [ ("scancode-licensedb", "scancode")
                           , ("osi", "osi")
                           , ("spdx", "spdx")
                           ]
    case lookup aliasScope knownAliasScopes of
        Just knwonScope ->map (newNLN knwonScope) <$> parseJSON aliases
        Nothing -> map (newNLN (K.toText aliasScope)) <$> parseJSON aliases

parseAliases :: Value -> Parser [LicenseName]
parseAliases = withObject "aliases" $ \v -> concat <$> mapM parsePair (KM.toList v)

instance FromJSON LicenseLynx where
    parseJSON = withObject "LicenseLynx" $ \o -> do
        licenseLynxCanonical <- setNS "LicenseLynx" <$> o .: "canonical"
        aliases <- o .: "aliases"
        licenseLynxAliases <- parseAliases aliases
        licenseLynxSrc <- o .: "src"
        return LicenseLynx { licenseLynxCanonical, licenseLynxAliases, licenseLynxSrc }


instance LicenseFactC LicenseLynx where
    getType _ = "LicenseLynx"
    getApplicableLNs (LicenseLynx {licenseLynxCanonical, licenseLynxAliases}) = LN licenseLynxCanonical `AlternativeLNs` map LN licenseLynxAliases

    -- (LN . newNLN "scancode" . pack . _key) scd
    --   `AlternativeLNs` [ (LN . newLN . pack . _shortName) scd,
    --                      (LN . newLN . pack . _name) scd
    --                    ]
    getImpliedStmts = mempty


newtype LicenseLynxData = LicenseLynxData FilePath

instance HasOriginalData LicenseLynxData where
    getOriginalData (LicenseLynxData dir) =
        FromUrl "https://github.com/licenselynx/licenselynx" $
            FromFile dir NoPreservedOriginalData

instance Source LicenseLynxData where
    getSource _ = Source "LicenseLynx"
    getSourceDescription _ = Just "Map license references found in the wild to canonical license identifiers." 
    getFacts (LicenseLynxData dir) = do
        jsons <- glob (dir </> "*.json")
        V.fromList <$> mapM (fmap wrapFact . getEntry) jsons

getEntry :: FilePath -> IO LicenseLynx
getEntry json = do
    logFileReadIO json
    let id = takeBaseName (takeBaseName json)
    decoded <- eitherDecodeFileStrict json :: IO (Either String LicenseLynx)
    case decoded of
        Left err -> fail err
        Right licenseLynx -> return licenseLynx
