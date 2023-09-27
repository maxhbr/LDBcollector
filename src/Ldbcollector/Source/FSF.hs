{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.Source.FSF
  ( FSF (..),
  )
where

import Data.ByteString (ByteString)
import Data.ByteString.Char8 qualified as Char8
import Data.Map qualified as Map
import Data.Vector qualified as V
import Ldbcollector.Model hiding (ByteString)

data FsfWkingData = FsfWkingData
  { _id :: LicenseName,
    _identifiers :: Map.Map Text [LicenseName],
    _name :: LicenseName,
    _tags :: [String],
    _uris :: [String]
  }
  deriving (Show, Eq, Ord, Generic)

instance FromJSON FsfWkingData where
  parseJSON = withObject "FsfWkingData" $ \v ->
    FsfWkingData
      <$> (newNLN "fsf" <$> v .: "id")
      <*> v .:? "identifiers" .!= mempty
      <*> v .: "name"
      <*> v .:? "tags" .!= []
      <*> v .:? "uris" .!= []

instance ToJSON FsfWkingData

instance LicenseFactC FsfWkingData where
  getType _ = "FSF"
  getApplicableLNs (FsfWkingData {_id = id, _identifiers = identifiers, _name = name}) =
    LN id `AlternativeLNs` [LN name] `ImpreciseLNs` concatMap (\(scope, lns) -> map (LN . setNS scope) lns) (Map.assocs identifiers)
  getImpliedStmts entry =
    map (LicenseUrl Nothing) (_uris entry)
      ++ map
        ( \case
            "libre" -> LicenseRating (PositiveLicenseRating "FSF" "Libre" NoLicenseRatingText)
            "gpl-2-compatible" -> LicenseRating (NeutralLicenseRating "FSF" "gpl-2-compatible" NoLicenseRatingText)
            "gpl-3-compatible" -> LicenseRating (NeutralLicenseRating "FSF" "gpl-3-compatible" NoLicenseRatingText)
            "non-free" -> LicenseRating (NegativeLicenseRating "FSF" "non-free" NoLicenseRatingText)
            tag -> stmt tag
        )
        (_tags entry)

parseFsfJSON :: FilePath -> IO FsfWkingData
parseFsfJSON json = do
  logFileReadIO json
  decoded <- eitherDecodeFileStrict json :: IO (Either String FsfWkingData)
  case decoded of
    Left err -> fail err
    Right fsfWkingData -> return fsfWkingData

newtype FSF = FSF FilePath

instance HasOriginalData FSF where
  getOriginalData (FSF dir) =
    FromUrl "https://www.gnu.org/licenses/license-list.html" $
      FromUrl "https://github.com/wking/fsf-api/" $
        FromUrl "https://github.com/wking/fsf-api/tree/gh-pages" $
          FromFile dir NoPreservedOriginalData

instance Source FSF where
  getSource _ = Source "FSF"
  getFacts (FSF dir) = do
    jsons <- (fmap (filter (not . isSuffixOf "licenses-full.json") . filter (not . isSuffixOf "licenses.json")) . glob) (dir </> "*.json")
    V.fromList . wrapFacts <$> mapM parseFsfJSON jsons
