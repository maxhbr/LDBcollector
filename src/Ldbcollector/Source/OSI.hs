{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Ldbcollector.Source.OSI
    ( OSI (..)
    ) where

import           Ldbcollector.Model
import qualified Data.Vector           as V
import qualified Data.Map              as Map
import qualified Data.Yaml as Y
import qualified Data.Yaml.Internal as Y

data OSILicense
    = OSILicense
    { _id :: LicenseName
    , _name :: String
    , _identifiers :: [LicenseName]
    , _keywords :: [String]
    , _links :: [(String,String)]
    , _other_names :: [(LicenseName, Maybe Text)]
    , _superseded_by :: Maybe LicenseName
    -- , _text :: [_]
    } deriving (Eq, Ord, Show, Generic)
instance FromJSON OSILicense where
  parseJSON = withObject "OSILicense" $ \v -> OSILicense
    <$> v .: "id"
    <*> v .: "name"
    <*> v .: "identifiers"
    <*> v .: "keywords"
    <*> v .: "links"
    <*> v .: "other_names"
    <*> v .: "superseded_by"
instance ToJSON OSILicense

instance LicenseFactC OSILicense where
    getType _ = "OSILicense"
    getApplicableLNs l = NLN (_id l)

getOSILicense :: FilePath -> IO [OSILicense]
getOSILicense yaml = do
    putStrLn ("read " ++ yaml)
    decoded <- Y.decodeFileEither yaml :: IO (Either Y.ParseException OSILicense)
    case decoded of
        Left err -> do
            putStrLn ("ERROR: " ++ show err)
            return []
        Right d  -> return [d]

newtype OSI = OSI FilePath

instance Source OSI where
    getOrigin _ = Origin "OSI"
    getFacts (OSI dir) = do
        yamls <- glob (dir </> "**/*.json")
        V.fromList . map wrapFact . mconcat <$> mapM getOSILicense yamls
