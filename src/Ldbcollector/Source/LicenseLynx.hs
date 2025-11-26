{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Ldbcollector.Source.LicenseLynx where

import Data.Aeson
import Data.Aeson.Types (Object, Parser, withObject)
import Data.Aeson.Key (Key)
import Data.Aeson.KeyMap qualified as KM
import Data.Aeson.Key qualified as K
import Data.Text (Text)
import Data.Vector qualified as V
import Ldbcollector.Model


data LicenseLynx = LicenseLynx {
    licenseLynxCanonical :: LicenseName,
    licenseLynxAliases :: [LicenseName]
} deriving (Show, Eq, Generic)

instance ToJSON LicenseLynx where
    toJSON = genericToJSON defaultOptions { fieldLabelModifier = camelTo2 '_' }

parseCanonical :: Value -> Parser LicenseName
parseCanonical = withObject "canonical" $ \o -> do
    cid <- o .: "id"
    msrc <- o .:? "src"
    case msrc of
        Just src -> return (parseOne (K.fromText src, cid))
        _ -> return (newNLN "LicenseLynx" cid)

parseOne :: (Key,Text) -> LicenseName
parseOne (aliasScope, alias) = do
    let knownAliasScopes = [ ("scancode-licensedb", "scancode")
                           , ("scancodeLicensedb", "scancode") 
                           , ("osi", "osi")
                           , ("spdx", "spdx")
                           , ("pypi", "pypi")
                           , ("pypi-classifer", "pypi")
                           ]
    case lookup aliasScope knownAliasScopes of
        Just knwonScope -> newNLN knwonScope alias
        Nothing -> newNLN (K.toText aliasScope) alias

parsePair :: (Key, Value) -> Parser [LicenseName]
parsePair ("custom", aliases) = 
    (fmap (map newLN) . parseJSON) aliases
    -- withArray "aliases" $ fmap (map (newNLN "custom")) . mapM parseJSON
parsePair (aliasScope, aliases) = map (\alias -> parseOne (aliasScope, alias))  <$> parseJSON aliases

parseAliases :: Value -> Parser [LicenseName]
parseAliases = withObject "aliases" $ \v -> concat <$> mapM parsePair (KM.toList v)

instance FromJSON LicenseLynx where
    parseJSON = withObject "LicenseLynx" $ \o -> do
        canonical <- o .: "canonical"
        licenseLynxCanonical <- parseCanonical canonical
        aliases <- o .: "aliases"
        licenseLynxAliases <- parseAliases aliases
        return LicenseLynx { licenseLynxCanonical, licenseLynxAliases }


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
