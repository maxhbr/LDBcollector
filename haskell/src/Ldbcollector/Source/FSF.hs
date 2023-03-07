{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.FSF
    ( FSF (..)
    ) where

import           Ldbcollector.Model    hiding (ByteString)

import           Data.ByteString       (ByteString)
import qualified Data.ByteString.Char8 as Char8
import qualified Data.Vector           as V
import qualified Data.Map as Map

data FsfWkingData
    = FsfWkingData
    { _id :: String
    , _identifiers :: Map.Map String [String]
    , _name :: String
    , _tags :: [String]
    , _uris :: [String]
    } deriving (Show, Generic)
instance FromJSON FsfWkingData where
  parseJSON = withObject "FsfWkingData" $ \v -> FsfWkingData
    <$> v .: "id"
    <*> v .:? "identifiers" .!= mempty
    <*> v .: "name"
    <*> v .:? "tags" .!= []
    <*> v .:? "uris" .!= []
instance ToJSON FsfWkingData

applyFsfWkingData :: FsfWkingData -> LicenseGraphTask
applyFsfWkingData d = let
        identifiersToTask = ( Adds . V.fromList . map LicenseName . concatMap (\(ns,names) -> map (newNLN (pack ns) . pack) names) . Map.toList . _identifiers) d
    in  Edge (AddTs . V.fromList $
            [ Add $ (Vec . map fromString) (_uris d)
            , Add $ (Vec . map fromString) (_tags d)
        ]) AppliesTo $
            Edge (fromValue d
                (LicenseName . newNLN "fsf" . pack . _id)
                (const Nothing)) Same identifiersToTask

applyJson :: FilePath -> IO LicenseGraphTask
applyJson json = do
    putStrLn ("read " ++ json)
    decoded <- eitherDecodeFileStrict json :: IO (Either String FsfWkingData)
    case decoded of
      Left err           -> fail err
      Right fsfWkingData -> return $ applyFsfWkingData fsfWkingData

newtype FSF = FSF FilePath

instance Source FSF where
    getTask (FSF dir) = do
        jsons <- (fmap (filter (not . isSuffixOf "licenses-full.json") . filter (not . isSuffixOf "licenses.json")) . glob) (dir </> "*.json")
        AddTs . V.fromList <$> mapM applyJson jsons