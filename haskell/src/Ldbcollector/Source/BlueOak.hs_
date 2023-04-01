{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
module Ldbcollector.Source.BlueOak
  ( BlueOakCouncil (..)
  ) where

import           MyPrelude
import           Ldbcollector.Model

import qualified Data.Vector as V
import qualified Data.Map as M
import qualified Data.ByteString
import qualified Data.ByteString.Lazy as B
import           Data.ByteString.Lazy (ByteString)


data BlueOakLicense
 = BlueOakLicense
 { _name :: String
 , _id :: String
 , _url :: String
 } deriving (Show,Generic)
instance FromJSON BlueOakLicense where
  parseJSON = withObject "BlueOakLicense" $ \v -> BlueOakLicense
    <$> v .: "name"
    <*> v .: "id"
    <*> v .: "url"
instance ToJSON BlueOakLicense

-- #############################################################################
-- #  permissive  ##############################################################
-- #############################################################################

data BlueOakRating
 = BlueOakRating
 { _rating :: String
 , _licenses :: [BlueOakLicense]
 } deriving (Show,Generic)
instance FromJSON BlueOakRating where
  parseJSON = withObject "BlueOakRating" $ \v -> BlueOakRating
    <$> v .: "name"
    <*> v .: "licenses"

data BlueOakData
  = BlueOakData
  { _version :: String
  , _ratings :: [BlueOakRating]
  } deriving (Show,Generic)
instance FromJSON BlueOakData where
  parseJSON = withObject "BlueOakData" $ \v -> BlueOakData
    <$> v .: "version"
    <*> v .: "ratings"

-- #############################################################################
-- #  copyleft  ################################################################
-- #############################################################################

data BlueOakCopyleftGroup
  = BlueOakCopyleftGroup
  { _bocgName :: String
  , _versions :: [BlueOakLicense]
  } deriving (Show,Generic)
instance FromJSON BlueOakCopyleftGroup where
  parseJSON = withObject "BlueOakCopyleftGroup" $ \v -> BlueOakCopyleftGroup
    <$> v .: "name"
    <*> v .: "versions"
data BlueOakCopyleftData
  = BlueOakCopyleftData
  { _bocgVersion :: String
  , _families :: Map String [BlueOakCopyleftGroup]
  } deriving (Show,Generic)
instance FromJSON BlueOakCopyleftData where
  parseJSON = withObject "BlueOakCopyleftData" $ \v -> BlueOakCopyleftData
    <$> v .: "version"
    <*> v .: "families"

-- #############################################################################
-- #  general  #################################################################
-- #############################################################################

data BlueOakCouncil
     = BlueOakCouncilLicenseList FilePath
     | BlueOakCouncilCopyleftList FilePath

getTaskForLicense :: BlueOakLicense -> LicenseGraphTask
getTaskForLicense (BlueOakLicense name id url) = 
    EdgeLeft ((Add . fromString) url) AppliesTo $
    Edge ((Add . LicenseName . newNLN "blueoak" . pack) id) Same$
    EdgeUnion ((Add . LicenseName . newLN . pack) name) Same ((Add . LicenseName . newLN . pack) id)

getTaskForLicenseList :: BlueOakData -> LicenseGraphTask
getTaskForLicenseList (BlueOakData _ ratings) = let
        ratingToTask (BlueOakRating rating licenses) = 
            Edge ((Add . fromString) rating) AppliesTo $
            (AddTs . V.fromList . map getTaskForLicense) licenses
    in Edge ((Add . fromString) "Permissive") AppliesTo $
            (AddTs . V.fromList . map ratingToTask) ratings

getTaskForCopyleftList :: BlueOakCopyleftData -> LicenseGraphTask
getTaskForCopyleftList (BlueOakCopyleftData _ families) = let
        groupToTask (BlueOakCopyleftGroup bocgName versions) = 
            Edge ((Add . LicenseName . newLN . pack) bocgName) (Potentially Better) $
                (AddTs . V.fromList . map getTaskForLicense) versions
        kindToTask (copyleftKind, copyleftGroups) = 
            Edge ((Add . fromString) copyleftKind) AppliesTo $
                (AddTs . V.fromList . map groupToTask) copyleftGroups
    in Edge ((Add . fromString) "Copyleft") AppliesTo $
            (AddTs . V.fromList . map kindToTask . M.assocs) families

instance Source BlueOakCouncil where
    getTask (BlueOakCouncilLicenseList file) = do
        decoded <- eitherDecodeFileStrict file :: IO (Either String BlueOakData)
        case decoded of
            Left err  -> fail err
            Right bod -> return $ getTaskForLicenseList bod
    getTask (BlueOakCouncilCopyleftList file) = do
        decoded <- eitherDecodeFileStrict file :: IO (Either String BlueOakCopyleftData)
        case decoded of
            Left err   -> fail err
            Right bocd -> return $ getTaskForCopyleftList bocd