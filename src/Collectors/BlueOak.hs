{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
module Collectors.BlueOak
  ( loadBlueOakFacts
  , loadBlueOakFactsFromString
  , decodeBlueOakData -- for testing
  ) where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Text as T
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)

import           Model.License

data BlueOakLicense
 = BlueOakLicense
 { name :: String
 , boId :: String
 , url :: String
 } deriving (Show,Generic)
instance FromJSON BlueOakLicense
instance ToJSON BlueOakLicense

data BlueOakRating
 = BlueOakRating
 { rating :: String
 , licenses :: [BlueOakLicense]
 } deriving (Show)
instance FromJSON BlueOakRating where
  parseJSON = withObject "BlueOakRating" $ \v -> BlueOakRating
    <$> v .: "name"
    <*> v .: "licenses"

data BlueOakData
  = BlueOakData
  { version :: String
  , ratings :: [BlueOakRating]
  } deriving (Show,Generic)
instance FromJSON BlueOakData where
  parseJSON = withObject "BlueOakData" $ \v -> BlueOakData
    <$> v .: "version"
    <*> v .: "ratings"

decodeBlueOakData :: ByteString -> BlueOakData
decodeBlueOakData bs = case decode bs of
  Just bod -> bod
  Nothing  -> trace "ERR: Failed to parse Blue Oak JSON" (BlueOakData "-1" [])

data BOEntry
  = BOEntry String -- licenseListVersion
            String -- rating
            BlueOakLicense -- data
  deriving Generic
instance ToJSON BOEntry where
  toJSON (BOEntry llv r l) = object [ "BlueOakRating" .= r, "name" .= (name l), "id" .= (boId l), "url" .= (url l), "isPermissive" .= True ]
instance Show BOEntry where
  show (BOEntry _ _ j) = show j

instance LFRaw BOEntry where
  getLicenseFactClassifier _               = LFC ["BlueOak", "BOEntry"]
  getImpliedNames (BOEntry _ _ bol)        = [boId bol]
  getImpliedStatements boe@(BOEntry _ r _) = V.singleton . FactStatement (getLicenseFactClassifier boe) $ IsPermissiveStatement True (Just ("rating is: " `T.append` (T.pack r)))

loadBlueOakFactsFromString :: ByteString -> Facts
loadBlueOakFactsFromString bs = let
    bod = decodeBlueOakData bs
    bodVersion = version bod
    bodRatings = ratings bod
    ratingConverter (BlueOakRating r ls) = map (LicenseFact . BOEntry bodVersion r) ls
    facts = concatMap ratingConverter bodRatings
  in trace ("INFO: the version of BlueOak is: " ++ bodVersion) $ V.fromList facts

-- example filepath: ../data/Blue_Oak_Council/blue-oak-council-license-list.json
loadBlueOakFacts :: FilePath -> IO Facts
loadBlueOakFacts blueOakFile = do
  s <- B.readFile blueOakFile
  return (loadBlueOakFactsFromString s)
